# Tempo AI

[Tempo AI](https://github.com/lgm42/tempo-ai) forecasts the French Tempo electricity tariff color
(blue, white or red) two to four days ahead, while RTE only publishes the next day. A small LightGBM
model predicts the national net load from the weather forecast, then the official RTE rules turn it
into a color. All data is public (RTE eCO2mix, Open-Meteo, api-couleur-tempo.fr) and the model is
trained locally on the CPU, no GPU needed.

On the first start the app downloads about ten years of history and trains its models, which takes
around 10 minutes. Every day it stores its own D+2, D+3 and D+4 forecasts and compares them with the
real colors, so the web page and the REST API (/api/summary) show its success rate overall, this
month and over the last 7 days.

A [Home Assistant integration](https://github.com/lgm42/ha-tempo-ai) (HACS) reads the same API and
creates the color, remaining-days and success-rate entities.
