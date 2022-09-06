
import pandas as pd

def convert_dtypes(df=None, data_types=None):

    if not isinstance(df, pd.DataFrame):
        print("""Please convert data into a Pandas DataFrame.""")

    df = df.copy()

    for col in df.columns:
        if col in data_types.keys():
            field = data_types[col]

            if field == 'Text':
                df[col] = df[col].astype(str)

            elif field == 'Numeric':
                df[col] = pd.to_numeric(df[col])

            elif field == 'DateTime':
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

            elif field == 'Url':
                df[col] = df.apply(lambda img: json.loads(img[col].replace("'","\"")), axis=1)

            else:
                pass

    df = df.where(pd.notnull(df), None)
    df = df.replace('NaT','None')

    return df.to_dict(orient='records')

def to_dataframe(records=None):

    df = pd.DataFrame.from_records(records)

    return df

