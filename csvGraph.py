#python stl
import plotly.graph_objects as go
from pandas import read_csv
#from plotly.subplots import make_subplots
from plotly import offline
from typing import List, TextIO
import re
import os

#local libs
import myLogger as log
import mySSH2

#declares our CSV files and serializes them
def serializeCSV(sensorName: List, sensorData: List):
    # save our working directory so we can ch back into it later
    workingDirectory = os.getcwd()
    log.makeDir("../csv")

    # pre declare the csv files so they are properly formatted
    sensorNumber = 0
    while sensorNumber < len(sensorName):
        if not os.path.exists("{}.csv".format(sensorName[sensorNumber])):
            csv = log.OpenFile("{}.csv".format(sensorName[sensorNumber]), "a+")
            log.myFileWrite(csv, '{},{}\n'.format("time", sensorName[sensorNumber]))
            log.myFileClose(csv)
        sensorNumber += 1

    # appends data to csv files
    sensorNumber = 0
    while sensorNumber < len(sensorName):
        if sensorData[sensorNumber] == " No Reading":
            sensorNumber += 1
            continue
        data = re.search("[-+]?\d*\.?\d+", sensorData[sensorNumber]).group(0)
        csv = log.OpenFile("{}.csv".format(sensorName[sensorNumber]), "a+")
        temp = "{},{}\n".format(log.timeStampSec(), data)
        log.myFileWrite(csv, temp)
        log.myFileClose(csv)
        sensorNumber += 1
    # return to our working directory and continue with checking thresholds
    os.chdir(workingDirectory)


def generateGraph(csvName: str, client: mySSH2.paramiko.SSHClient) -> None:
    sensorName = re.search("[^\.]+", csvName).group(0)
    #pull the axis names from the csv
    file = log.OpenFile(csvName, "r")
    xaxis, yaxis = file.readline().split(",")
    log.myFileClose(file)

    #have plotly interpret the data
    data = read_csv(csvName)

    fig = go.Figure()

    #add the sensor data line
    fig.add_trace(
        go.Scatter(
            x = data[xaxis], y = data[yaxis.replace("\n", "")],
            name=sensorName
        )
    )
    #redetermine the thresholds for each sensors
    thresholds = {
        "UNR" : re.search('\d.+', mySSH2.sendCommand(client, "ipmitool sdr get '" + sensorName + "'  | grep 'Upper non-recoverable'")),
        "UC" : re.search('\d.+', mySSH2.sendCommand(client, "ipmitool sdr get '" + sensorName + "' | grep 'Upper critical'")),
        "UNC" : re.search('\d.+', mySSH2.sendCommand(client, "ipmitool sdr get '" + sensorName + "'  | grep 'Upper non-critical'")),
        "LNR" : re.search('\d.+', mySSH2.sendCommand(client, "ipmitool sdr get '" + sensorName + "'  | grep 'Lower non-recoverable'")),
        "LC" : re.search('\d.+', mySSH2.sendCommand(client, "ipmitool sdr get '" + sensorName + "'  | grep 'Lower critical'")),
        "LNC" : re.search('\d.+', mySSH2.sendCommand(client, "ipmitool sdr get '" + sensorName + "'  | grep 'Lower non-critical'"))
    }
    shapes = []
    #add threshold lines
    for threshold in thresholds:
        if thresholds[threshold]:
            shape = go.layout.Shape(
                type="line",
                xref="paper",
                x0=0,
                y0=thresholds[threshold].group(0),
                x1=1,
                y1=thresholds[threshold].group(0),
                line=dict(
                    color= "red",
                    width=4,
                    dash="dashdot"
                )

            )
            shapes.append(shape)

#give the graph some formatting and titles
    fig.update_layout(
        shapes = tuple(shapes),
        title="{} vs {}".format(yaxis, xaxis),
        xaxis_title=xaxis, yaxis_title=yaxis,
        showlegend=True,
    )

    offline.plot(fig, filename="{}.html".format(sensorName), auto_open=False)