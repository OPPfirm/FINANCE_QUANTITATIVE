#import Library
from datetime import datetime
import pandas as pd

import MetaTrader5  as mt5


#initialize the bonds between Metatrader 5 and Python
mt5.initialize()

#Fonction to download Database From this moment and number of data (candlestick)
def get_rates(symbol, number_of_data=10000, timeframe=mt5.TIMEFRAME_D1):
    """Fonction to download Database From this moment and some tick before"""

   #Library
    import pandas as pd
    import MetaTrader5 as mt5
    from datetime import datetime

    #compute date now
    from_date= datetime.now()

    #extra n rates befors now
    rates= mt5.copy_rates_from(symbol=symbol,timeframe=timeframe,date_from=from_date,count=number_of_data)

    #Transform array into a DataFrame
    rates=pd.DataFrame(rates)

    #convert a nulmber format of the date into date format
    df_rates["time"]= pd.to_datetime(rates["time"], unit="s")

    #put column "time" like the index of our DataSet
    df_rates=df_rates.set_index("time")

    return df_rates


# Fonction to download Database between range date (candlesick)
def get_rates_range(symbol, from_date, to_date=None, timeframe=mt5.TIMEFRAME_D1):
    if to_date is None:
        to_date = datetime.now()

    if from_date >= to_date:
        raise ValueError("from_date must be before to_date")

    try:
        rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
        df_rates = pd.DataFrame(rates)

        if df_rates.empty:
            print("No data received.")
            return df_rates

        df_rates["time"] = pd.to_datetime(df_rates["time"], unit="s")
        df_rates.set_index("time", inplace=True)
        return df_rates

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

"""
# Exemple d'utilisation
try:
    if not mt5.initialize():
        print("❌ Failed to initialize MetaTrader5")
    else:
        df = get_rates_range("EURUSD", datetime(2025, 4, 1), datetime(2025, 4, 30))

        print(df.head())

        save_path = input("Write the path to store the file if you want to (if not, just press enter): ")
        if save_path.strip():
            df.to_csv(save_path)

finally:
    mt5.shutdown()
    
"""


"""
Parfait, tu veux donc extraire dynamiquement le nom du broker via l’API de MetaTrader5 (et non pas l’écrire toi-même dans "EURUSD:Admiral"). ✅

🎯 Objectif :
Générer un nom de fichier du type EURUSD_M30_Admiral.csv,
en récupérant le broker directement via MetaTrader5, pas à la main.

✅ Étape 1 : Récupérer le nom du broker
Tu peux utiliser la fonction suivante :

python
Copier le code
account_info = mt5.account_info()
broker_name = account_info.company  # Par exemple "Admiral Markets AS"
Tu peux ensuite faire un petit nettoyage si tu veux raccourcir le nom :

python
Copier le code
broker_name = broker_name.replace(" ", "").replace("Markets", "").strip()
# Exemple : "AdmiralMarkets AS" → "AdmiralAS"
✅ Code complet adapté à ton besoin :
python
Copier le code
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd

def get_rates(symbol, number_of_data=10000, timeframe=mt5.TIMEFRAME_D1):
    from_date = datetime.now()
    rates = mt5.copy_rates_from(symbol, timeframe, from_date, number_of_data)
    df_rates = pd.DataFrame(rates)
    df_rates["time"] = pd.to_datetime(df_rates["time"], unit="s")
    df_rates = df_rates.set_index("time")
    return df_rates

def get_timeframe_str(timeframe):
    for attr in dir(mt5):
        if attr.startswith("TIMEFRAME_") and getattr(mt5, attr) == timeframe:
            return attr.replace("TIMEFRAME_", "")
    return str(timeframe)

# === Utilisation ===
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M30

try:
    if not mt5.initialize():
        print("❌ Failed to initialize MetaTrader5")
    else:
        df = get_rates(symbol, number_of_data=3000, timeframe=timeframe)
        print(df.head())

        # Récupérer le nom du broker via l'API
        account_info = mt5.account_info()
        broker_name = account_info.company if account_info else "UnknownBroker"

        # Nettoyage du nom (facultatif)
        broker_name = broker_name.split()[0]  # Garde juste "Admiral", par exemple

        tf_str = get_timeframe_str(timeframe)
        filename = f"{symbol}_{tf_str}_{broker_name}.csv"

        save_path = input("Chemin pour enregistrer (laisser vide pour dossier actuel) : ").strip()
        full_path = save_path + "/" + filename if save_path else filename

        df.to_csv(full_path)
        print(f"✅ Données sauvegardées dans : {full_path}")

finally:
    mt5.shutdown()
✅ Résultat automatique :
Si tu es connecté à un compte Admiral Markets, ça te génèrera :

Copier le code
EURUSD_M30_Admiral.csv
Souhaites-tu ajouter aussi la date (comme EURUSD_M30_Admiral_20250512.csv) ?
"""