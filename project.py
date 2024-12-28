import engi1020.arduino.api as engi #for readings
import matplotlib.pyplot as plt #graphing 
import time,json, smtplib, os #used for file storing, email sending
from hidden import user, password  #used for my email and password, in a different file for privacy

def email_fun(): 
    #Make variables useable in other spots in code
    global email
    global choice

    #Ask if user wants to use email
    while True:
        choice = input("Would you like to recieve your alerts in an email/sms? Reply with Y/N : ")
        if choice.isalpha():
            break
        else:
            print("Please enter a valid letter")
            continue
    
    #Input email based off of the choice user inputs
    while True:
        if choice == "Y" or choice == "y":
            while True:
                email = input("Please enter your email or number: ")
                if "@" not in email or "." not in email:
                    print("That is not a valid email address")
                else:
                    return True
        elif choice == "N" or  choice == "n":
            return False
        else:
            print("Please enter either Y/N ")
            continue
    

def readings():
    data = []
    for i in range(10):
        humiditiy = engi.temp_humid_get_humidity(3) #Returns in RH%
        temperature = engi.temp_humid_get_temp(3) #Returns in Celcius
        pressure = engi.pressure_get_pressure() #Returns Pa (Pascals)
        data.append({"Humidity" : f"{humiditiy}", "Temperature" : f"{temperature}", "Pressure" : f"{pressure}"})
    return data

def thresholds(readings):
    message = """\
            Subject: *WARNING* *TAKE ACTION IMMEDIATELY*

            THIS IS A WARNING

            THE AIR QUALITY NEAR YOU IS CURRENTLY NOT SUITABLE TO BE IN
            PLEASE MOVE TO A DIFFERENT AREA TO KEEP SAFE
            """

    # Flatten the list if it is nested
    if len(readings) == 1 and isinstance(readings[0], list):
        readings = readings[0]

    
    # Define thresholds
    temp_min = 20  # Minimum acceptable temperature (°C)
    temp_max = 25  # Maximum acceptable temperature (°C)
    pressure_min = 300  # Minimum acceptable pressure (hPa)
    pressure_max = 400  # Maximum acceptable pressure (hPa)
    humidity_min = 35 #Minimum acceptable humidity (RH%)
    humidity_max = 55 #Maximum acceptable humidity (RH%)

    # List to store readings that exceed thresholds
    exceeded_readings = []

    # Check each reading against thresholds
    for reading in readings:
        temp = float(reading["Temperature"])
        pressure = float(reading["Pressure"])
        humidity = float(reading["Humidity"])

        # Check if the reading is outside acceptable ranges
        exceeded = {}
        if temp < temp_min or temp > temp_max:
            exceeded["Temperature"] = f"{temp}°C (Threshold: {temp_min}-{temp_max}°C)"
        if pressure < pressure_min or pressure > pressure_max:
            exceeded["Pressure"] = f"{pressure} hPa (Threshold: {pressure_min}-{pressure_max} hPa)"
        if humidity < humidity_min or humidity > humidity_max:
            exceeded["Humidity"] = f"{humidity} RH (Threshold: {humidity_min}-{humidity_max} RH) "
        # If any threshold is exceeded, add the reading and exceeded values
        if exceeded:
            exceeded_readings.append({
                "Reading": reading,
                "Exceeded": exceeded
            })

    if exceeded_readings: #this can work, but also if exceeded_readings since if there is stuff in list, it is true; false if blank
        if choice.lower() == 'y':
            alerts(choice,email)
            print(message)
        else:
            alerts(choice) #since no email argument, email is kept = None
        print(message)

    else:
        print("No values exceeded the thresholds! ")

# Function to save readings to a JSON file
def save_text(read=None):
    filename = "readings_saved.json"
    if read is None:
        read = readings()  # Collect new readings (list of dictionaries)

    # Ensure the file exists or create it with an empty list
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump([], file)

    # Load existing data
    with open(filename, "r") as file:
        data = json.load(file)

    # Correctly extend the list with new readings
    if isinstance(read, list):
        data.extend(read)
    else:
        data.append(read)

    # Save updated data back to the file
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    print("Data saved successfully!")


# Function to load and display data from the file
def load_text():
    filename = "readings_saved.json"
    

    # Check if the file exists
    if not os.path.exists(filename):
        print("No data to load. File does not exist.")
        return []

    # Load and return the data
    with open(filename, "r") as file:
        data = json.load(file)
        print("Data loaded successfully!")

    # Flatten the list if nested
    flattened_data = []
    for item in data:
        if isinstance(item, list):  # If `item` is a list, extend the main list
            flattened_data.extend(item)
        else:  # If `item` is a dictionary, add it directly
            flattened_data.append(item)
    return data
    
    
def graph_data():
    data = load_text()  # Load the data

    # Flatten the data if it's nested
    if len(data) == 1 and isinstance(data[0], list):
        data = data[0]

    # Extract temperature and pressure
    temperatures = [float(entry["Temperature"]) for entry in data if "Temperature" in entry]
    pressures = [float(entry["Pressure"]) for entry in data if "Pressure" in entry]
    humidities = [float(entry["Humidity"]) for entry in data if "Humidity" in entry]
    timestamps = range(1, len(data) + 1)  # Create x-axis as 1, 2, 3, ...

    # Check for empty data
    if not temperatures or not pressures or not humidities:
        print("Error: No valid temperature, pressure, or humidity data to plot.")
        return

    # Plot the data
    plt.figure(figsize=(10, 6))

    # Temperature plot
    plt.subplot(3, 1, 1)
    plt.plot(timestamps, temperatures, marker="o", color="blue", label="Temperature (°C)")
    plt.xlabel("Reading Number")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature Over Time")
    plt.grid(True)
    plt.legend()

    # Pressure plot
    plt.subplot(3, 1, 2)
    plt.plot(timestamps, pressures, marker="s", color="red", label="Pressure (hPa)")
    plt.xlabel("Reading Number")
    plt.ylabel("Pressure (hPa)")
    plt.title("Pressure Over Time")
    plt.grid(True)
    plt.legend()

    # Humidity plot
    plt.subplot(3,1,3)
    plt.plot(timestamps, humidities, marker="D", color="green", label="Humidity (RH%)")
    plt.xlabel("Reading Number")
    plt.ylabel("Humidity (RH%)")
    plt.title("Relative Humidity Over Time")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()



def alerts(choice, email=None):    
    sender_email = user()
    sender_password = password()
    if email is not None:
        #send data to "email"
        if choice == "y" or "Y":
            if len(email) > 0:
                message = """\
                Subject: *WARNING* *TAKE ACTION IMMEDIATELY*

                THIS IS A WARNING

                THE AIR QUALITY NEAR YOU IS CURRENTLY NOT SUITABLE TO BE IN
                PLEASE MOVE TO A DIFFERENT AREA TO KEEP SAFE
                """
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls() 
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message)
                server.quit()

    
    engi.buzzer_frequency(5, 500)
    time.sleep(2)
    engi.buzzer_stop(5)


#email_fun()
#data = readings()
#save_text(data)
#thresholds(data)
#print(load_text())
graph_data()
