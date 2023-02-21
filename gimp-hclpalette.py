from gimpfu import *
import math

def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)

def empty_input():
    try:
        input("Press Enter to continue...")
    except:
        pass

def to_linear(color):
    #https://entropymine.com/imageworsener/srgbformula/
    if color <= 0.0404482362771082:
        return color/12.92
    else:
        return pow(((color+0.055)/1.055), 2.4)

def from_linear(color):
    #https://entropymine.com/imageworsener/srgbformula/
    if color <= 0.00313066844250063:
        return color*12.92
    else:
        return pow(color, 0.4166666666666667)*1.055-0.055

def rgb_xyz(pixel):  # sRGB
    input_pixel = list(pixel)
    output_pixel = [0, 0, 0]
    #http://brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    xyz_matrix = [[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]]
    for counter in range(len(input_pixel)):
        input_pixel[counter] = to_linear(input_pixel[counter]/255.0)
    for row_num in range(len(xyz_matrix)):
        for colomn_num in range(len(xyz_matrix[0])):
            output_pixel[row_num] = output_pixel[row_num] + (xyz_matrix[row_num][colomn_num] * (input_pixel[colomn_num]))
    return tuple(output_pixel)

def xyz_rgb(pixel, need_int = False):  #sRGB
    result = [0, 0, 0]
    #http://brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    inverse_xyz_matrix = [[3.2404542, -1.5371385, -0.4985314],
                          [-0.9692660, 1.8760108, 0.0415560],
                          [0.0556434, -0.2040259, 1.0572252]]
    for row_num in range(len(inverse_xyz_matrix)):
        for colomn_num in range(len(inverse_xyz_matrix[0])):
            result[row_num] = result[row_num] + ((inverse_xyz_matrix[row_num][colomn_num] * (pixel[colomn_num])))
    for counter in range(len(result)):
        result[counter] = int(round(from_linear(result[counter])*255.0)) if need_int else from_linear(result[counter])*255.0
    return tuple(result)

def xyz_lab(pixel):
    #http://brucelindbloom.com/index.html?LContinuity.html
    epsilon = 216.0/24389.0
    kappa = 24389.0/27.0
    #https://en.wikipedia.org/wiki/Illuminant_D65 !whitepoint
    x_white = 0.95047
    y_white = 1.00000
    z_white = 1.08883
    #http://brucelindbloom.com/index.html?Eqn_XYZ_to_Lab.html
    x_r = pixel[0]/x_white
    y_r = pixel[1]/y_white
    z_r = pixel[2]/z_white
    func_xyz_result = [0,0,0]
    counter = 0
    for r in (x_r, y_r, z_r):
        func_xyz_result[counter] = pow(r, 1.0/3.0) if r > epsilon else (kappa*r+16.0)/116.0
        counter = counter+1
    l = 116.0*func_xyz_result[1]-16.0
    a = 500.0*(func_xyz_result[0]-func_xyz_result[1])
    b = 200.0*(func_xyz_result[1]-func_xyz_result[2])
    return (l,a,b)

def lab_xyz(pixel):
    #http://brucelindbloom.com/index.html?LContinuity.html
    epsilon = 216.0/24389.0
    kappa = 24389.0/27.0
    #https://en.wikipedia.org/wiki/Illuminant_D65 !whitepoint
    x_white = 0.95047
    y_white = 1.00000
    z_white = 1.08883
    #http://brucelindbloom.com/index.html?Eqn_Lab_to_XYZ.html
    func_y_result = (pixel[0]+16.0)/116.0
    func_x_result = (pixel[1]/500.0)+func_y_result
    func_z_result = func_y_result-(pixel[2]/200.0)
    x = x_white*pow(func_x_result, 3) if pow(func_x_result, 3) > epsilon else ((116.0*func_x_result-16.0)/kappa)*x_white
    y = y_white*pow(((pixel[0]+16.0)/116.0), 3.0) if pixel[0] > kappa*epsilon else (pixel[0]/kappa)*y_white
    z = z_white*pow(func_z_result, 3) if pow(func_z_result, 3) > epsilon else (116.0*func_z_result-16.0)/kappa
    return (x,y,z)

def lab_lch(pixel):
    #http://brucelindbloom.com/index.html?Eqn_XYZ_to_Lab.html
    l = pixel[0]
    c = pow((pow(pixel[1], 2)+pow(pixel[2], 2)), 1.0/2.0)
    arctan = math.degrees(math.atan2(pixel[2],pixel[1])) if pixel[1] !=0 else 0
    h = arctan if arctan >= 0 else arctan+360.0
    return (l,c,h)

def lch_lab(pixel):
    #http://brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    l = pixel[0]
    a = math.cos(math.radians(pixel[2]))*pixel[1]
    b = math.sin(math.radians(pixel[2]))*pixel[1]
    return (l,a,b)

def rgb_hsv(pixel):
    red = pixel[0]/255.0
    green = pixel[1]/255.0
    blue = pixel[2]/255.0
    minimum = min(red, green, blue)
    maximum = max(red, green, blue)
    value_raw = maximum*100.0
    chroma = maximum-minimum
    saturation_raw = 0.0 if maximum == 0.0 else chroma*100.0/maximum
    if chroma == 0:
        hue_temp = 0.0
    elif maximum == red:
        hue_temp = 60.0*(0.0+(green-blue)/chroma)
    elif maximum == green:
        hue_temp = 60.0*(2.0+(blue-red)/chroma)
    elif maximum == blue:
        hue_temp = 60.0*(4.0+(red-green)/chroma)
    hue_raw = ((hue_temp + 360.0) % 360.0)
    hsv_pixel_raw = (hue_raw, saturation_raw, value_raw)
    return(hsv_pixel_raw)

def hsv_rgb(pixel, need_int = False):
    hue = pixel[0]
    saturation = pixel[1]
    value = pixel[2]
    sat_norm = saturation/100.0
    val_norm = value/100.0
    chroma = val_norm*sat_norm
    hue_part = hue/60.0
    temp_color = chroma*(1-abs(((hue_part%2)-1)))
    color_offset = val_norm - chroma
    if math.floor(hue_part) == 0:
        red, green, blue = chroma+color_offset, temp_color+color_offset, 0+color_offset
    elif math.floor(hue_part) == 1:
        red, green, blue = temp_color+color_offset, chroma+color_offset, 0+color_offset
    elif math.floor(hue_part) == 2:
        red, green, blue = 0+color_offset, chroma+color_offset, temp_color+color_offset
    elif math.floor(hue_part) == 3:
        red, green, blue = 0+color_offset, temp_color+color_offset, chroma+color_offset
    elif math.floor(hue_part) == 4:
        red, green, blue = temp_color+color_offset, 0+color_offset, chroma+color_offset
    elif math.floor(hue_part) == 5:
        red, green, blue = chroma+color_offset, 0+color_offset, temp_color+color_offset
    rgb_pixel_raw = red*255, green*255, blue*255
    rgb_pixel = int(round(red*255)), int(round(green*255)), int(round(blue*255))

    if need_int:
        return(rgb_pixel)
    else:
        return(rgb_pixel_raw)

def value_gradient_row(timg, tdrawable, lowest_value, y):
    width = pdb.gimp_image_width(timg)
    pixel_tuple = pdb.gimp_drawable_get_pixel(tdrawable, 0, y)
    pixel = pixel_tuple[1]
    hsv_pixel = rgb_hsv(pixel)
    if lowest_value > hsv_pixel[2]:
        lowest_value = hsv_pixel[2]
    step = (hsv_pixel[2]-lowest_value)/(width-1)
    value = hsv_pixel[2]-step
    coord_temp = 1
    while coord_temp < width:
        pdb.gimp_drawable_set_pixel(tdrawable, coord_temp, y, 3, hsv_rgb((hsv_pixel[0],hsv_pixel[1],value), True))
        value = value-step
        coord_temp = coord_temp+1

def color_spread(timg, tdrawable, initial_luminance, initial_chroma):
    height = pdb.gimp_image_height(timg)-1
    step = 360.0/height
    hue_temp = 0
    for y in range (0, height, 1):
        pdb.gimp_drawable_set_pixel(tdrawable, 0, y, 3, xyz_rgb(lab_xyz(lch_lab((initial_luminance, initial_chroma, hue_temp))), True))
        hue_temp = hue_temp+step
    pdb.gimp_drawable_set_pixel(tdrawable, 0, height, 3, xyz_rgb(lab_xyz(lch_lab((initial_luminance, 0, 0))), True))

def value_gradient(timg, tdrawable, lowest_value, zero_saturation_minimum_value_offset):
    height = pdb.gimp_image_height(timg)-1
    for y in range(0, height, 1):
        value_gradient_row(timg, tdrawable, lowest_value, y)
    value_gradient_row(timg, tdrawable, clamp((lowest_value+zero_saturation_minimum_value_offset), 0, 100), height)

def luminance_fix_by_column(timg, tdrawable): # just checking
    for x in range(pdb.gimp_image_width(timg)):
        average_luminance = 0
        for y in range(pdb.gimp_image_height(timg)-1):
            pixel = lab_lch(xyz_lab(rgb_xyz((pdb.gimp_drawable_get_pixel(tdrawable, x, y)[1]))))
            average_luminance = average_luminance + pixel[0]
        average_luminance = average_luminance/pdb.gimp_image_height(timg)
        for y in range(pdb.gimp_image_height(timg)-1):
            pixel = lab_lch(xyz_lab(rgb_xyz((pdb.gimp_drawable_get_pixel(tdrawable, x, y)[1]))))
            pdb.gimp_drawable_set_pixel(tdrawable, x, y, 3, xyz_rgb(lab_xyz(lch_lab((average_luminance, pixel[1], pixel[2]))), True))

def plugin_main(timg, tdrawable, initial_luminance, lowest_value, zero_saturation_minimum_value_offset, initial_chroma):
    color_spread(timg, tdrawable, initial_luminance, initial_chroma)
    value_gradient(timg, tdrawable, lowest_value, zero_saturation_minimum_value_offset)
    luminance_fix_by_column(timg, tdrawable)

register(

        "python_fu_hcl_palette_generator",
        "1. Fill leftmost column with evenly picked colors of desired luminance.\n2. Add gradient through image width for each color to picked darkest.\n3. Same for BnW (0 saturation), with optional offset in darkest.                                                                                                            ",
        "1. Fill leftmost column with evenly picked colors of desired luminance.\n2. Add gradient through image width for each color to picked darkest.\n3. Same for BnW (0 saturation), with optional offset in darkest.                                                                                                            ",
        "gorg",
        "gorg",
        "2020",
        "<Image>/Image/Generate palette using HCL...",
        "*",
        [
        (PF_SLIDER, "initial-luminance", "Initial luminance value: ", 75, (0, 100, 1)),
        (PF_SLIDER, "lowest-value", "Minimum HSV \"Value\" value for all colors: ", 9, (0, 100, 1)),
        (PF_SLIDER, "zero-saturation-minimum-value-offset", "Minimum \"Value\" value for zero saturation: ", -3, (-20, 20, 1)),
        (PF_SLIDER, "initial-chroma", "Initial chtoma value: ", 38, (0, 100, 1))
        ],
        [],

        plugin_main)

main()