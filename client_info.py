class ClientInfo:
    clientOptions = ["Name", "Age", "Gender", "Date of Birth", "Date of Sample", "Examiner Name", "Sampling Context"]
    infoArray = []
    
    def __init__(self):
        for option in self.clientOptions:
            self.infoArray.append("")
            
    def submitInfo(self, infoEntryText: str, clicked: str):
        for i, option in enumerate(self.clientOptions):
            if clicked == option:
                self.infoArray[i] = infoEntryText
    
    def __str__(self):
        string = ""
        for x in range(len(self.clientOptions)):
            if self.infoArray[x] != '':
                infoText = self.clientOptions[x] + ": " + self.infoArray[x] + "\n"
                string += infoText
        return string