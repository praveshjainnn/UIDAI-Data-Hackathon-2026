# Helper to filter dataframes
def filter_df(df, state, district):
    dff = df.copy()
    if state:
        dff = dff[dff['State'] == state]
    if district:
        # Handle cases where District column might reference a different name or be missing in some merged views
        # But for our main CSVs (loc, soc, emp, ind), 'District' exists.
        dff = dff[dff['District'] == district]
    return dff
