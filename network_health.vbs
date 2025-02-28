Dim objFSO, objExcel, objWorkbook, objSheet
Dim serialPort, filePath, row
Dim cpuUsage, temp, signalStrength, packetLoss, errorLog
Dim objComm, objShell

' Define file path
filePath = "D:\Apps by Hashir\Network Health Prediction\network-data.xlsx"

' Define COM Port (Change as needed)
serialPort = "COM3"

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")

' Create Excel Application
Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = True

' Check if Excel file exists, create if not
If objFSO.FileExists(filePath) Then
    Set objWorkbook = objExcel.Workbooks.Open(filePath)
Else
    Set objWorkbook = objExcel.Workbooks.Add
    objWorkbook.SaveAs filePath
End If

Set objSheet = objWorkbook.Sheets(1)

' Set headers if file is new
If objSheet.Cells(1,1).Value = "" Then
    objSheet.Cells(1,1).Value = "Timestamp"
    objSheet.Cells(1,2).Value = "CPU Usage (%)"
    objSheet.Cells(1,3).Value = "Temperature (°C)"
    objSheet.Cells(1,4).Value = "Signal Strength (dBm)"
    objSheet.Cells(1,5).Value = "Packet Loss (%)"
    objSheet.Cells(1,6).Value = "Error Log"
End If

' Find next empty row
row = objSheet.UsedRange.Rows.Count + 1

' Initialize MSComm to read from COM port
On Error Resume Next
Set objComm = CreateObject("MSCommLib.MSComm")
If Err.Number <> 0 Then
    objSheet.Cells(row,1).Value = Now
    objSheet.Cells(row,6).Value = "ERROR: MSComm32 not installed"
    objWorkbook.Save
    objExcel.Quit
    WScript.Echo "ERROR: MSComm32 library not installed."
    WScript.Quit
End If
Err.Clear
On Error Resume Next

' Configure COM Port
objComm.CommPort = 3
objComm.Settings = "9600,N,8,1"
objComm.PortOpen = True

If objComm.PortOpen = False Then
    objSheet.Cells(row,1).Value = Now
    objSheet.Cells(row,6).Value = "ERROR: No device found on " & serialPort
    objWorkbook.Save
    objExcel.Quit
    WScript.Echo "ERROR: No device connected to " & serialPort
    WScript.Quit
End If

' Read Data Loop
Do While True
    If objComm.InBufferCount > 0 Then
        line = objComm.Input
        data = Split(line, ",")
    
        If UBound(data) >= 3 Then
            cpuUsage = CDbl(data(0))
            temp = CDbl(data(1))
            signalStrength = CDbl(data(2))
            packetLoss = CDbl(data(3))
        Else
            cpuUsage = "N/A"
            temp = "N/A"
            signalStrength = "N/A"
            packetLoss = "N/A"
        End If

        ' Determine health status
        If IsNumeric(cpuUsage) And IsNumeric(temp) And IsNumeric(signalStrength) And IsNumeric(packetLoss) Then
            If cpuUsage < 50 And temp < 45 And signalStrength > -60 And packetLoss < 1 Then
                errorLog = "System operating normally."
            ElseIf cpuUsage > 65 And cpuUsage < 80 Then
                errorLog = "Warning: CPU load increasing, possibly due to higher network demands or background processes."
            ElseIf cpuUsage >= 80 Then
                errorLog = "Critical: CPU overload detected. Possible reasons: Too many processes or insufficient resources."
            ElseIf temp > 60 Then
                errorLog = "Critical: Overheating! Ensure the system is properly ventilated and check for dust buildup."
            ElseIf signalStrength < -75 Then
                errorLog = "Weak signal detected. Likely cause: Poor connection, interference, or distance from router."
            ElseIf packetLoss > 5 Then
                errorLog = "Warning: High packet loss. Likely cause: Network congestion or faulty cables."
            Else
                errorLog = "Unknown system state. Please check system parameters."
            End If
        Else
            errorLog = "ERROR: Invalid data received from serial port. Please check connections."
        End If

        ' Log data to Excel
        objSheet.Cells(row,1).Value = Now
        objSheet.Cells(row,2).Value = cpuUsage
        objSheet.Cells(row,3).Value = temp
        objSheet.Cells(row,4).Value = signalStrength
        objSheet.Cells(row,5).Value = packetLoss
        objSheet.Cells(row,6).Value = errorLog
        row = row + 1

        ' Save after each entry
        objWorkbook.Save
    End If
    WScript.Sleep 1000  ' Wait 1 second before next reading
Loop

' Cleanup
objComm.PortOpen = False
Set objComm = Nothing
objWorkbook.Close True
objExcel.Quit
Set objWorkbook = Nothing
Set objExcel = Nothing
Set objFSO = Nothing
