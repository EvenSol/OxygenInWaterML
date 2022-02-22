from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from neqsim.thermo.thermoTools import fluid_df
from neqsim.process import stream,  compressor
import pandas as pd

class oxygenInWater(BaseModel):

    oxygen: float=0.01
    pressure: float=0.9
    temperature: float=0.1
    
    def calcOxygenInWater(self):
        gascondensate = {
            'ComponentName':  ["nitrogen", "oxygen", "water"], 
            'MolarComposition[-]':  [1.0-self.oxygen, self.oxygen, 1.0], 
          }
        gascondensateFluid = fluid_df(pd.DataFrame(gascondensate), lastIsPlusFraction=False)
        gascondensateFluid = gascondensateFluid.autoSelectModel()
        gascondensateFluid.autoSelectMixingRule();
        gascondensateFluid.setPressure(self.pressure, "bara")
        gascondensateFluid.setTemperature(self.temperature, "C")
        inStream = stream(gascondensateFluid)
        inStream.run()
        return [inStream.getFluid().getPhase('aqueous').getComponent('oxygen').getx()*1e6]

class compressorResults(BaseModel):
    oxygenInWater: float


app = FastAPI()

@app.get("/")
def read_root():
    html_content = """
    <html>
        <head>
            <title>NeqSim Live - Oxygen in Water</title>
        </head>        <body>
            <h1>NeqSim Live API for Calculation of Oxygen in Water</h1>
            <a href="/docs">API documentation and testing</a><br>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

 
@app.post("/ml3/calcOxygenInWater",response_model=compressorResults,description="Calculate oxygen solubility in water")
def calcOxygenInWater(oxCalc:oxygenInWater):
    calcRes = oxCalc.calcOxygenInWater()
    results = {
        'oxygenInWater': float(calcRes[0])
    }
    return results