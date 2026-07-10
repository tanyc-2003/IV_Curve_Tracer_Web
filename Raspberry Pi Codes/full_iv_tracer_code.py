'''

    ***** Summer Internship - IV Curve Tracer *****

    Install the pigpio library:
        sudo apt-get install pigpio python3-pigpio

    Initiate pigpiod daemon:
        sudo systemctl start pigpiod

    Or set pigpiod daemon at boot
        sudo systemctl enable pigpiod


    ************************************************
    Author:
    Tan Yi Cherng
    Cheng Zhi Meng
    Tan Wei Jun

'''

from PIL import Image, ImageDraw, ImageFont
import ST7735 as TFT
import pigpio
import requests
import time
import json
import spidev
import matplotlib .pyplot as plt
import csv


pi = pigpio.pi() # initialise pigpio

#########################################################################
#########################################################################
#########################################################################
############################  LCD CODE  #################################
#########################################################################
#########################################################################
#########################################################################

# Constants for display dimensions and SPI configuration
WIDTH, HEIGHT = 128, 160
SPEED_HZ = 4000000
DC, RST = 24, 25  # Raspberry Pi configuration
SPI_PORT, SPI_DEVICE = 0, 1


def init_display():
    spi_handle2 = pi.spi_open(SPI_DEVICE, SPEED_HZ, 0)
    disp = TFT.ST7735(
        DC,
        rst=RST,
        spi=spi_handle2,  # Pass the pigpio spi handle
        pi=pi  # Pass the pigpio instance for managing GPIO
    )
    disp.begin()
    disp.clear((0, 0, 0))  # Clear the display to black
    return disp

# Drawing functions
def draw_outline(draw):
    """Draws the outline on the display."""
    outline_color = (74, 212, 255)
    draw.line((0, 1, 128, 1), fill=outline_color, width=2)    # Top outline
    draw.line((2, 0, 2, 160), fill=outline_color, width=2)    # Left outline
    draw.line((126, 0, 126, 160), fill=outline_color, width=2) # Right outline
    draw.line((0, 158, 128, 158), fill=outline_color, width=2) # Bottom outline

def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    """Draws rotated text on the image."""
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    rotated = textimage.rotate(angle, expand=1)
    image.paste(rotated, position, rotated)

def zm_point(draw, position, colour, size):
    """Draws a point or square of given size."""
    for x in range(size):
        for y in range(size):
            draw.point((position[0] + x, position[1] + y), fill=colour)

def zm_arrow(draw, position, colour, direction='360'):
    """Draws an arrow on the display."""
    offsets = [(0, 2), (-2, 0), (-4, -2), (2, 0), (4, -2)]
    for offset in offsets:
        if direction == '360':
            zm_point(draw, (position[0] + offset[0], position[1] + offset[1]), colour, 2)
        elif direction == '90':
            zm_point(draw, (position[0] + offset[1], position[1] + offset[0]), colour, 2)

# # Power calculation functions
# def multiplication(array_I, array_V):
#     """Calculates power array by element-wise multiplication of current and voltage arrays."""
#     return [a * b for a, b in zip(array_I, array_V)]

# def find_highest_value(array, array_I, array_V):
#     """Finds the highest power and corresponding current and voltage values."""
#     highest_value = max(array)
#     highest_index = array.index(highest_value)
#     value_from_array_I = array_I[highest_index]
#     value_from_array_V = array_V[highest_index]
#     return highest_value, value_from_array_I, value_from_array_V

# def sort(array_I, array_V):
#     """Sorts the power array and finds the maximum values."""
#     array_P = multiplication(array_I, array_V)
#     return find_highest_value(array_P, array_I, array_V)


def find_Vmpp_Impp (curve_data):
    p_list = []
    for i in range(len(curve_data)):
        p_list.append(round(curve_data[i][1],1) * round(curve_data[i][2],1))

    if p_list:
        mpp_list = [] # [V,I]
        max_P = max(p_list)
        max_p_index = p_list.index(max_P)

        mpp_list = [round(curve_data[max_p_index][1],1), round(curve_data[max_p_index][2],1)]
    
    else:
        mpp_list =[0,0]

    return mpp_list

# Design functions for pages
axis_x, axis_y = 17, 35
arrow_x, arrow_y  = 140, 105
axis_x_len = arrow_x-axis_x # length of X axis 
axis_y_len = arrow_y-axis_y # length of Y axis 

# Algorith to plot the curve
def lcd_list_process(Voc: float, Isc: float, arg_dict, step_x = axis_x_len-5, step_y = axis_y_len-5, n=1) -> list:

    v_temp = Voc / step_x
    i_temp = Isc / step_y
    v_step = v_temp

    global lcd_processed_list
    lcd_processed_list = []
    ref_voltage_list = []
    exit_counter=0

    if arg_dict:
        for i in range(len(arg_dict)-1):
            ref_voltage_list.append(round(arg_dict[i][1], 1))
        
        #filter some annoying values
        ref_v_index=0
        for y in range(len(ref_voltage_list)):
            if ref_v_index > 1 and ref_v_index + 2 < len(ref_voltage_list):
                if (ref_voltage_list[ref_v_index] < ref_voltage_list[ref_v_index+1]) and (ref_voltage_list[ref_v_index] < ref_voltage_list[ref_v_index+2]):
                    del ref_voltage_list[ref_v_index]
                    print(f'removed: {ref_voltage_list[ref_v_index]}')
                    ref_v_index -=1
            
            ref_v_index +=1

        
        x=len(arg_dict)-1

        lcd_processed_list.append(abs(round(arg_dict[x][2] / i_temp + axis_y)))
        lcd_processed_list.append(abs(round(arg_dict[x][1] / v_temp + axis_x)))


        while len(lcd_processed_list) <= axis_x_len*2 and x>=0:

            if round(v_step,1) in ref_voltage_list:
                if round(arg_dict[x][1],1) == round(v_step,1):
                    lcd_processed_list.append(abs(round(arg_dict[x][2] / i_temp + axis_y)) )
                    lcd_processed_list.append(abs(round(arg_dict[x][1] / v_temp + axis_x)) )
                    
                    if round(arg_dict[x][1],1) != round(arg_dict[x-1][1],1) or round(arg_dict[x][1],1) < round(arg_dict[x-1][1],1):
                        n += 1
                        v_step = v_temp * n

                x-=1

            else:
                n += 1
                v_step = v_temp * n

                exit_counter += 1
                if exit_counter >=100:
                    break

        lcd_processed_list.append(abs(round(arg_dict[0][2] / i_temp + axis_y)))
        lcd_processed_list.append(abs(round(arg_dict[0][1] / v_temp + axis_x)))
        
    
    print(ref_voltage_list)
    print(lcd_processed_list)
    return lcd_processed_list

def lcd_list_process_power_curve(Voc: float, Isc: float, arg_dict):
    power_dict = {}

    if arg_dict:
        for i in range(len(arg_dict)-1):
            power_dict[i] = [arg_dict[i][0], arg_dict[i][1], arg_dict[i][1]*arg_dict[i][2]]

    print(power_dict)

    return lcd_list_process(Voc, (I_mpp*V_mpp), power_dict)
    

# Page 1
def pg1(draw, curve_data):

    global lcd_processed_list
    global V_oc, I_sc, V_mpp, I_mpp

    V_oc = curve_data[0][1] if curve_data else 0
    I_sc = curve_data[(len(curve_data)-1)][2] if curve_data else 0
    mpp = find_Vmpp_Impp(curve_data)
    V_mpp = mpp[0]
    I_mpp = mpp[1]

    """Draws page 1 on the display."""

    draw.line((21, 0, 21, 160), fill=(74, 212, 255), width=2)                    # Split line

    fontext= ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)
    font_bottom_text = ImageFont.load_default()
    draw_rotated_text(disp.buffer, 'I_sc = ', (8, 15), 270, fontext, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'V_oc = ', (8, 85), 270, fontext, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, "{:.2f}".format(I_sc), (9, 45), 270, fontext, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, "{:.2f}".format(V_oc), (9, 120), 270, fontext, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'I', (arrow_y + 6, axis_x - 5), 270, font_bottom_text, fill=(51, 51, 255))
    # draw_rotated_text(disp.buffer, '/', (arrow_y + 6, axis_x - 1), 270, font_bottom_text, fill=(255, 255, 255))
    # draw_rotated_text(disp.buffer, 'P', (arrow_y + 6, axis_x + 5), 270, font_bottom_text, fill=(255, 51, 51))
    draw_rotated_text(disp.buffer, 'V', (axis_y - 3, arrow_x + 6), 270, font_bottom_text, fill=(255, 255, 255))

    lg_x, lg_y = 135, 100
    draw_rotated_text(disp.buffer, 'I', (lg_y + 15, lg_x + 12), 270, font_bottom_text, fill=(51, 51, 255))
    # draw_rotated_text(disp.buffer, 'P', (lg_y + 5, lg_x + 12), 270, font_bottom_text, fill=(255, 51, 51))
    draw.line((lg_y + 19, lg_x, lg_y + 19, lg_x + 10), fill=(51, 51, 255), width=2)
    # draw.line((lg_y + 9, lg_x, lg_y + 9, lg_x + 10), fill=(255, 51, 51), width=2)

    # Replace NumPy's linspace with a list comprehension
    iv_curve_lcd = lcd_list_process(V_oc, I_sc, curve_data)
    draw.line(iv_curve_lcd,fill=(51,51,255),width=2)
    # pv_curve_lcd = lcd_list_process_power_curve(V_oc, I_sc, curve_data)
    # draw.line(pv_curve_lcd,fill=(255, 51, 51),width=2)

    draw.line((axis_y, axis_x, axis_y, arrow_x), fill=(255, 255, 255), width=2)  # Y-axis
    draw.line((axis_y, axis_x, arrow_y, axis_x), fill=(255, 255, 255), width=2)  # X-axis
    zm_arrow(draw, (arrow_y, axis_x), colour=(255, 255, 255), direction='90')    # X-axis arrow
    zm_arrow(draw, (axis_y, arrow_x), colour=(255, 255, 255))                    # Y-axis arrow

    draw.line((lcd_processed_list[0] if lcd_processed_list else 0,15,lcd_processed_list[0] if lcd_processed_list else 0,20),fill=(255,255,255),width=2) # intersection line - y
    draw.line((33,lcd_processed_list[-1] if lcd_processed_list else 0,38,lcd_processed_list[-1] if lcd_processed_list else 0),fill=(255,255,255),width=2) # intersection line - x
    #zm_point(draw,((xx/88)+17,(yy/105)+35),colour=(255, 255, 255),size=2)

# Page 2
def pg2(draw):

    global V_oc, I_sc, V_mpp, I_mpp, Power, P_max, FF

    Power = (I_sc*V_oc)
    P_max = (I_mpp*V_mpp)
    FF = ((P_max/Power) if Power else 0)

    """Draws page 2 on the display."""
    font_bottom_text = ImageFont.load_default()
    y = -16
    draw_rotated_text(disp.buffer, '1. I_sc', (y + 126, 5), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, '2. V_oc', (y + 105, 5), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, '3. P_max', (y + 84, 5), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, '4. Fill Factor, FF', (y + 63, 5), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, '5. I_mpp', (y + 42, 5), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, '6. V_mpp', (y + 21, 5), 270, font_bottom_text, fill=(255, 255, 255))

    draw.line((21, 5, 21, 155), fill=(74, 212, 255), width=2)
    draw.line((42, 5, 42, 155), fill=(74, 212, 255), width=2)
    draw.line((63, 5, 63, 155), fill=(74, 212, 255), width=2)
    draw.line((84, 5, 84, 155), fill=(74, 212, 255), width=2)
    draw.line((105, 5, 105, 155), fill=(74, 212, 255), width=2)
    draw.line((126, 5, 126, 155), fill=(74, 212, 255), width=2)
    draw.line((0, 120, 128, 120), fill=(74, 212, 255), width=2)

    draw_rotated_text(disp.buffer, "{:.2f}".format(I_sc), (y + 126, 125), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, "{:.2f}".format(V_oc), (y + 105, 125), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, "{:.2f}".format(P_max), (y + 84, 125), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, "{:.2f}".format(FF), (y + 63, 125), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, "{:.2f}".format(I_mpp), (y + 42, 125), 270, font_bottom_text, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, "{:.2f}".format(V_mpp), (y + 21, 125), 270, font_bottom_text, fill=(255, 255, 255))

disp = init_display()
draw = disp.draw()
draw_outline(draw)



#########################################################################
#########################################################################
#########################################################################
############################  MAIN CODE  ################################
#########################################################################
#########################################################################
#########################################################################

#########################################################################
#########################  Global Variables  ############################
#########################################################################

I_sc = 0
V_oc = 0
Power = 0
I_mpp = 0
V_mpp = 0
P_max = 0
FF = 0

long_press = False;
single_press = False;
long_press_time = 1.5  # seconds for a long press

duty_cycle = 0
gain = 0
dc_step = 0.2 # Step of duty cycle from 0 to 100 
gain_step = 0.04 # Step of gain 
sweep_delay_time = 0.01 # Sleep time on each step - in second
num_read_adc = 4 # Measured and averaged over 10

val_dict={}
current_key = 0

bus = 0
device_adc = 0
current_value_channel = 7
voltage_value_channel = 6

url = "https://iv-curve-tracer-web.onrender.com/dataPacketAvailable"
post_data = {}

page_num = 0

filtered_data = []
empty_data = []



#########################################################################
############################  Pin Setup  ################################
#########################################################################
# BCM numbering not BOARD numbering
###### Initialise ######
pwm_pin = 18 
butt_pin = 17
led1_pin = 22
led2_pin =27

###### Input Pin ######
pi.set_mode(butt_pin, pigpio.INPUT) # button
# pin_value = pi.read(input_pin)

###### Output Pin ######
pi.set_mode(led1_pin, pigpio.OUTPUT) # LED 1 - Red
pi.set_mode(led2_pin, pigpio.OUTPUT) # LED 2 - Green
pi.write(led1_pin, 0)
pi.write(led2_pin, 1)

###### Set PWM frequency and duty cycle on the specified pin ######
frequency = 45000
duty_cycle_scaled = duty_cycle * 10000

# Set PWM frequency and duty cycle on the specified pin
pi.hardware_PWM(pwm_pin, frequency, duty_cycle_scaled)

# GPIO 10 - PIN 19 (SPI0 MOSI)
# GPIO 9 - PIN 21 (SPI0 MISO)
# GPIO 11 - PIN 23 (SPI0 SCLK)

# GPIO 18 - PIN 12 (PCM CLK)

# GPIO 17 - PIN 11 (button)
# GPIO 23 - PIN 16 (LED 1 - Red)
# GPIO 24 - PIN 18 (LED 2 - Green)


#########################################################################
############################  FUNCTIONS  ################################
#########################################################################

# The duty_cycle range for hardware_PWM is 0-1,000,000
def scaled_dc(dc):
    global duty_cycle_scaled
    duty_cycle_scaled = int(dc * 10000)

###### Button Press ######
def button_pressed(gpio, level, tick):
    # gpio and tick will be passed automatically when callback is triggered
    global long_press
    global single_press

    if level == 1:  # Button pressed (active low)
        start_time = time.time()

        # Wait for the button release
        while pi.read(butt_pin) == 1:
            time.sleep(0.01)  # small sleep to reduce CPU usage

        press_duration = time.time() - start_time

        if press_duration > long_press_time:
            long_press = True
            single_press = False
            print("Long press detected")
        else:
            long_press = False
            single_press = True
            print("Single click detected")



###### Setup and open SPI bus 0, device 0(chip select) ######
def spi_connect(bus:int, device:int):
    global spi_handle
    # SPI0 - support 2 device (0,1)
    # SPI1 - support 3 device (0,1,2)
    spi_handle = pi.spi_open(device_adc, 3000000, 0)  # device: 0 for SPI0, 1 for SPI1, speed: 3.6MHz, mode: 0 (SPI0), 256 (SPI1)

###### Read adc ######
def read_adc(channel:int) -> float:
    channel = channel * 16 + 128
    send_data = [0x01, channel, 0x00]
    rx_data= pi.spi_xfer(spi_handle, send_data)[1]
    value = rx_data[1] * 256 + rx_data[2]
    return value * 5.0 / 1024

######  Average adc value ######
def avg_read_adc(num_samples:int,channel:int)->float:
    temp = 0.0
    for i in range(num_samples):
        temp+=read_adc(channel)
    return temp/num_samples

###### Sweep IV curve ######
def sweep():
    global current_key 
    global val_dict
    global duty_cycle
    global gain

    pi.hardware_PWM(pwm_pin, frequency, 0)
    current_offset = read_adc(current_value_channel)
    print(f'Current offset: {current_offset}')

    while duty_cycle < 100:

        scaled_dc(duty_cycle)
        pi.hardware_PWM(pwm_pin, frequency, duty_cycle_scaled)

        avg_voltage = avg_read_adc(num_read_adc, voltage_value_channel) *12

        avg_current = (avg_read_adc(num_read_adc, current_value_channel) - current_offset) * 10# negative becuase i connected the opposite

        val_dict[current_key]=[duty_cycle, avg_voltage,avg_current]
        print(val_dict[current_key])


        if(duty_cycle < 80 or duty_cycle >= 85):
            duty_cycle += dc_step
            gain = duty_cycle/(100-duty_cycle)

        elif (duty_cycle >= 80 or duty_cycle < 85):
            gain += gain_step
            duty_cycle = (gain/(1+gain)) * 100

        current_key+=1

        time.sleep(sweep_delay_time)


    current_key = 0
    duty_cycle = 0
    gain =0
    scaled_dc(duty_cycle)
    pi.hardware_PWM(pwm_pin, frequency, duty_cycle_scaled)
    

###### Data Analysis ######
#error means how much percentage of error we allow for current value before flagging it, 0.0<error<1.0
#val1 and val2 means the value of the previous and next element of val_dict with reference to the current value
#May be inaccurate near Voc/Isc since they have near-zero values, hence dc should start with some value like 2% and end before 100%
def compare(val1:float,val2:float,current_val:float,error:float)->bool:
    lower_bound=min(val1,val2)*(1-error)
    upper_bound=max(val1,val2)*(1+error)
    if(lower_bound<=current_val<=upper_bound):
        return False
    else:
        return True
    
#better_val_dict_process processes val_dict to flag extreme values then returns an updated dictionary
#repeat can be used to set how many times hte function is run on arg_dict,I would advise at least 2
#Scans avg_vol column first followed by avg_current column
#Returns a return_dict that only contains filtered key-value pairs            
def better_val_dict_process(arg_dict,error:float,repeat:int)->dict:
    temp_dict=arg_dict.copy()
    return_dict={}
    for r in range(repeat):
        flagged_list=[]
        skip=0
        return_key=0
        return_dict.clear()
        for col in range(1,3):
            for x in range(1,len(temp_dict)-1):
                if (skip>0):
                    skip-=1
                    continue
                if(compare(temp_dict[x-1][col],temp_dict[x+1][col],temp_dict[x][col],error)):
                    flagged_list.append(x)
                    skip=1
        for temp_dict_key in range(len(temp_dict)):
            if(temp_dict_key not in flagged_list):
                return_dict[return_key]=temp_dict[temp_dict_key]
                return_key+=1
        temp_dict=return_dict.copy()
    return return_dict


###### POST request ######
def POST_Req(post_data, timeout=5):
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, data=json.dumps(post_data), headers=headers, timeout=timeout)
        response.raise_for_status()
        print("POST Response Code:", response.status_code)
        print("POST Response Body:", response.text)
    except requests.exceptions.Timeout:
        print(f"POST request timed out after {timeout} seconds.")
    except requests.exceptions.RequestException as e:
        print(f"POST request failed: {e}")


        
###### CSV ######    
def writeToCSV(data, data_taken, data_remaining, sweep_end_time, compute_end_time):
    csv_name = 'rename'
    with open(csv_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        

        writer.writerow ([f'Data taken: {data_taken}'])
        writer.writerow([f'Data remaining: {data_remaining}'])
        writer.writerow([f'Sweep time: {sweep_end_time} s'])
        writer.writerow([f'Total computational time: {compute_end_time} s'])

        for key, valueList in data.items():
            writer.writerow([key] + valueList)
  
        
##### Test Plot #####
def plotGraph(data, name):
    #Test
        I_list =[]
        V_list =[]

        for x in range(len(data)):
            
            I_list.append(data[x][2])
            V_list.append(data[x][1])

        plt.figure(figsize=(8, 6))
        plt.plot(V_list, I_list, marker='o', linestyle='-')
        plt.title(name)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.grid(True)


#########################################################################
############################  Main Loop  ################################
#########################################################################

###### check button press ######
pi.callback(butt_pin, pigpio.RISING_EDGE, button_pressed)

lcd_processed_list = empty_data
disp.clear((0, 0, 0))
pg1(draw, lcd_processed_list)
disp.display() 

while True:

    ###### Enter scan mode (Long Press Button) ######
    if (long_press):

        print("Enter sweep mode")

        # Start scan
        pi.write(led1_pin, 1)
        pi.write(led2_pin, 0)

        # Sweep IV curve
        spi_connect(bus, device_adc)
        start_time = time.time() #debug
        sweep()
        sweep_end_time = time.time()-start_time #debug
        pi.spi_close(spi_handle)


        # Filter data
        filtered_data = better_val_dict_process(val_dict, 0.005, 10)
        compute_end_time = time.time()- start_time #debug


        # Debug
        # plotGraph(val_dict, 'unfiltered')
        # plotGraph(filtered_data, 'filtered')
        # plt.show()

        data_taken = len(val_dict)
        data_remaining = len(filtered_data)
        print (f'Data taken: {data_taken}')
        print(f'Data remaining: {data_remaining}')
        print(f'Sweep time: {sweep_end_time} s')
        print(f'Total computational time: {compute_end_time} s')


        # Write to csv
        # writeToCSV(filtered_data, data_taken, data_remaining, sweep_end_time, compute_end_time)


        # Update display (page 1)
        disp.clear((0, 0, 0))
        pg1(draw, filtered_data)
        disp.display()  

        # Send data to web
        POST_Req(filtered_data)

        # Completed scan
        pi.write(led1_pin, 0)
        pi.write(led2_pin, 1)

        print("Scan Complete")


        long_press = False


    ###### Change display (Single Press Button) ######
    if (single_press):

        page_num = 0 if page_num == 1 else 1
        print(f'Page changed: page_num = {page_num}')

        # Update display
        if (page_num):
            # Table page (page 2)
            print("Enter Page 2")
            disp.clear((0, 0, 0))
            pg2(draw)
            disp.display()  
        else:
            # Graph page (page 1)
            print("Enter Page 1")
            disp.clear((0, 0, 0))
            pg1(draw, filtered_data)
            disp.display()  

        single_press = False