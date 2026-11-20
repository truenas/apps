# Tempo AI

[Tempo AI](https://github.com/lgm42/tempo-ai) forecasts the French Tempo electricity tariff color
(blue, white or red) two to four days ahead, while RTE only publishes the next day. A small LightGBM
model predicts the national net load from the weather forecast, then the official RTE rules turn it
into a color. All data is public (RTE eCO2mix, Open-Meteo, api-couleur-tempo.fr) and the model is
trained locally on the CPU, no GPU needed.
