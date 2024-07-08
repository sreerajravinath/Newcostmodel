from fastapi import FastAPI, HTTPException, Request
import pandas as pd
import xlwings as xw
import json
import os

app = FastAPI()

@app.post('/process/{model_id}')
async def process_data(model_id: str, data: dict):
    try:
        models_directory = os.path.join(os.path.dirname(__file__), '..', 'models')
        with open(os.path.join(models_directory, f'model_{model_id}', 'config.json')) as f:
            config = json.load(f)

        with xw.App(visible=False) as app:
            wb = xw.Book(os.path.join(models_directory, f'model_{model_id}', config["excel_file"]))
            input_sheet = wb.sheets[config["input_sheet"]]
            for param, cell in config["input_locations"].items():
                input_sheet.range(cell).value = data.get(param)
            
            output_sheet = wb.sheets[config["output_sheet"]]
            result = {key: output_sheet.range(cell).value for key, cell in config["output_locations"].items()}
            wb.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/lookup_data/{model_id}/{field_name}')
async def lookup_data(model_id: str, field_name: str, request: Request):
    try:
        body = await request.json()
        models_directory = os.path.join(os.path.dirname(__file__), '..', 'models')
        with open(os.path.join(models_directory, f'model_{model_id}', 'config.json')) as f:
            config = json.load(f)

        lookup_config = config['lookup_columns'][field_name]
        column_range = lookup_config['column_range']
        remove_duplicates = lookup_config.get('remove_duplicates', False)
        filter_by = lookup_config.get('filter_by', {})

        with xw.App(visible=False) as app:
            wb = xw.Book(os.path.join(models_directory, f'model_{model_id}', config["excel_file"]))
            lookup_sheet = wb.sheets[config["lookup_sheet"]]

            if filter_by:
                reference_columns = filter_by.get('reference_columns', [filter_by.get('reference_column')])
                filters = []
                for ref_col in reference_columns:
                    ref_val = body.get(ref_col)
                    filters.append(f'{ref_col} == "{ref_val}"')
                filter_string = ' & '.join(filters)
                df = lookup_sheet.range(column_range).options(pd.DataFrame, header=1, index=False).value.query(filter_string)
            else:
                df = lookup_sheet.range(column_range).options(pd.DataFrame, header=1, index=False).value

            if remove_duplicates:
                df = df.drop_duplicates()

            result = df.to_dict(orient='records')
            wb.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
