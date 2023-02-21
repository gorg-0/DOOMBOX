#include <fstream>
#include <sstream>
#include <iostream>
#include <typeinfo>
#include <chrono>
#include <thread>

#include <opencv2/dnn.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>

#include <filesystem>
#include <windows.h>

#define DEBUG

#define BOUNDING_BOX_CENTER_X 0
#define BOUNDING_BOX_CENTER_Y 1
#define BOUNDING_BOX_WIDTH 2
#define BOUNDING_BOX_HEIGHT 3
#define FIRST_CONFIDENCE 5

double confidenceThreshold = 0.5; //QT to add interface? (+ notion)
float nmsThreshold = 0.4;

unsigned __int64 frameStartTime = 1;
unsigned __int64 frameEndTime = 1;

cv::Mat frame;
cv::Mat previewImage;
bool noMoreFrames = false;
cv::Mat blob;
std::vector<cv::Mat> darkNetOutput;
cv::Mat finalImage;

std::vector<std::string> getOutBlobNames(const cv::dnn::Net&);
void addFrameTimeToImage(cv::Mat, unsigned __int64);

void readNextFrame(cv::VideoCapture& capture, cv::Mat& frame, cv::Mat& previewImage, bool& noMoreFrames);
void generateBlob(cv::Mat& frame, cv::Mat& blob, bool& noMoreFrames);
void forwardDNN(std::vector<cv::Mat>& darkNetOutput, cv::dnn::Net& darkNet, cv::Mat& blob, std::vector<std::string>& outBlobNames, bool& noMoreFrames);
void getAndDrawBoundingBoxes(cv::Mat& previewImage, std::vector<cv::Mat>& darkNetOutput, bool& noMoreFrames);

std::condition_variable frameLock;

int main(int argc, char* argv[])
{

#ifdef DEBUG

    std::string filePath = "D:/Visual Studio Projects/OpenCV/Resources/example2.mp4";

#endif // DEBUG

#ifndef DEBUG

    if (argc == 1)
    {
        system("cls");
        std::cout << "Please drag a file on the EXE from the same folder." << std::endl;
        std::cout << "Press Enter to exit." << std::endl;
        std::cin.ignore(1);
        return 0;
    }

    std::string filePath = argv[1];

#endif // !DEBUG

    std::string yolo3config = "\\YOLO\\yolov3.cfg";
    std::string yolo3weight = "\\YOLO\\yolov3.weights";

    //initializing network
    cv::dnn::Net darkNet = cv::dnn::readNetFromDarknet(yolo3config, yolo3weight);
    darkNet.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);

    //darkNet.setPreferableTarget(cv::dnn::DNN_TARGET_OPENCL);
    darkNet.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);
    //darkNet.setPreferableTarget(cv::dnn::DNN_TARGET_CUDA);

    std::vector<std::string> outBlobNames = getOutBlobNames(darkNet);

    cv::VideoCapture capture(filePath);

    if (capture.isOpened())
    {

        capture.read(frame); //don't understand why i need this here for now, but it fixes some crashes

        std::thread readNextFrameThread(readNextFrame, std::ref(capture), std::ref(frame), std::ref(previewImage), std::ref(noMoreFrames));
        std::thread generateBlobThread(generateBlob, std::ref(frame), std::ref(blob), std::ref(noMoreFrames));
        std::thread forwardDNNThread(forwardDNN, std::ref(darkNetOutput), std::ref(darkNet), std::ref(blob), std::ref(outBlobNames), std::ref(noMoreFrames));
        std::thread getAndDrawBoundingBoxesThread(getAndDrawBoundingBoxes, std::ref(previewImage), std::ref(darkNetOutput), std::ref(noMoreFrames));

        //all of the threaded mess above saves 20-30ms

        while (noMoreFrames == false)
        {

        }

        readNextFrameThread.join();
        generateBlobThread.join();
        forwardDNNThread.join();
        getAndDrawBoundingBoxesThread.join();

    }
    else
    {
        system("cls");
        std::cout << "Wrong file." << std::endl;
        std::cout << "Press Enter to exit." << std::endl;
        std::cin.ignore(1);
        return 0;
    }

    return 0;
}

void readNextFrame(cv::VideoCapture& capture, cv::Mat& frame, cv::Mat& previewImage, bool& noMoreFrames) //should join frame and blob probably
{
    while (capture.isOpened())
    {

        if (!frame.empty())
        {
            continue;
        }

        if (!capture.read(frame))
        {
            noMoreFrames = true;
            system("cls");
            std::cout << "No more frames available." << std::endl;
            std::cout << "Press Enter to exit." << std::endl;
            std::cin.ignore(1);
            break;
        }

        previewImage = frame;

    }
}

void generateBlob(cv::Mat& frame, cv::Mat& blob, bool& noMoreFrames)
{
    while (true)
    {
        if (noMoreFrames == true)
        {
            break;
        }

        if (!blob.empty() || frame.empty())
        {
            continue;
        }
        cv::Mat tempFrame = frame;
        frame.release();
        cv::dnn::blobFromImage(tempFrame, blob, 1 / 255.0, cv::Size(416, 416), cv::Scalar(0, 0, 0), true, false); //needs reseach on best/optimal params (+notion)
    }
}

void forwardDNN(std::vector<cv::Mat>& darkNetOutput, cv::dnn::Net& darkNet, cv::Mat& blob, std::vector<std::string>& outBlobNames, bool& noMoreFrames)
{
    while (true)
    {
        if (noMoreFrames == true)
        {
            break;
        }

        if (!darkNetOutput.empty() || blob.empty())
        {
            continue;
        }
        cv::Mat tempBlob = blob;
        blob.release();
        darkNet.setInput(tempBlob);
        darkNet.forward(darkNetOutput, outBlobNames);
    }
}

void getAndDrawBoundingBoxes(cv::Mat& previewImage, std::vector<cv::Mat>& darkNetOutput, bool& noMoreFrames)
{
    while (true)
    {
        if (noMoreFrames == true)
        {
            break;
        }

        if (previewImage.empty() || darkNetOutput.empty())
        {
            continue;
        }

        std::vector<cv::Rect> boundingBoxes;
        std::vector<int> classIds;
        std::vector<float> confidences;

        cv::Mat tempPreviewImage = previewImage;
        previewImage.release();

        for (size_t outputMatsCounter = 0; outputMatsCounter < darkNetOutput.size(); ++outputMatsCounter)
        {

            for (size_t rowCounter = 0; rowCounter < darkNetOutput[outputMatsCounter].rows; ++rowCounter)
            {

                cv::Point classPointId;
                double confidence;

                minMaxLoc(darkNetOutput[outputMatsCounter].row(rowCounter).colRange(FIRST_CONFIDENCE, darkNetOutput[outputMatsCounter].cols), 0, &confidence, 0, &classPointId);

                if (confidence > confidenceThreshold)
                {
                    int boxCenterX = (int)(*(float*)darkNetOutput[outputMatsCounter].row(rowCounter).col(BOUNDING_BOX_CENTER_X).data * tempPreviewImage.cols);
                    int boxCenterY = (int)(*(float*)darkNetOutput[outputMatsCounter].row(rowCounter).col(BOUNDING_BOX_CENTER_Y).data * tempPreviewImage.rows);
                    int boxWidth = (int)(*(float*)darkNetOutput[outputMatsCounter].row(rowCounter).col(BOUNDING_BOX_WIDTH).data * tempPreviewImage.cols);
                    int boxHeight = (int)(*(float*)darkNetOutput[outputMatsCounter].row(rowCounter).col(BOUNDING_BOX_HEIGHT).data * tempPreviewImage.rows);

                    classIds.push_back(classPointId.x);
                    confidences.push_back((float)confidence);
                    boundingBoxes.push_back(cv::Rect((boxCenterX - boxWidth / 2), (boxCenterY - boxHeight / 2), boxWidth, boxHeight));
                }

            }

        }

        std::vector<int> indices;
        cv::dnn::NMSBoxes(boundingBoxes, confidences, confidenceThreshold, nmsThreshold, indices);

        //drawing boxes stars here
        for (size_t counter = 0; counter < indices.size(); ++counter)
        {
            int index = indices[counter];
            cv::Rect box = boundingBoxes[index];
            cv::rectangle(tempPreviewImage, cv::Point(box.x, box.y), cv::Point(box.x + box.width, box.y + box.height), cv::Scalar(255, 178, 50), 3);
        }

        frameEndTime = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();

        addFrameTimeToImage(tempPreviewImage, frameEndTime - frameStartTime);

        cv::imshow("FUCK", tempPreviewImage);
        cv::waitKey(1);
        darkNetOutput.clear();

        frameStartTime = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    }
}

std::vector<std::string> getOutBlobNames(const cv::dnn::Net& darkNet)
{

    std::vector<int> outLayers = darkNet.getUnconnectedOutLayers();

    std::vector<std::string> outBlobNames(outLayers.size());

    for (size_t i = 0; i < outBlobNames.size(); ++i)
    {
        outBlobNames[i] = darkNet.getLayerNames()[outLayers[i] - 1];
    }

    return outBlobNames;
}

void addFrameTimeToImage(cv::Mat sourceImage, unsigned __int64 lastFrameTime)
{
    std::string lastFrameTimeString;
    lastFrameTimeString = "Frame time in ms: " + std::to_string(lastFrameTime) + " FPS: " + std::to_string(1000 / lastFrameTime);
    cv::putText(sourceImage, lastFrameTimeString, cv::Point(10, sourceImage.rows / 2 + 30), cv::FONT_HERSHEY_DUPLEX, 1.0, CV_RGB(255, 255, 255), 2);
}