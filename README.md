# geopython

This repository illustrates simple use cases of choropleth maps visualization with Python.

## Content

* a notebook for interactive analysis
* a Streamlit app for interactive visualization

### Limitation with Google Colab

When working a city level for the whole France, map generation is taking too long and some timeout triggers stopping map rendering (at about 30 seconds). This seems to be a known issue with Google Colab. And no workaround was found, trying to extend this timeout.

To display city level maps, only one (or a limited set of) department(s) has to be selected. See notebook.

### Running the Streamlit app

Application should be started from the main directory:

```
streamlit run app/app.py
```

## Credits

Dataset from https://data.gouv.fr.

geojson files provided by https://github.com/gregoiredavid/france-geojson.
