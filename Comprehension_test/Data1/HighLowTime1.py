#import Library
import numpy as np
import pandas as pd
from tqdm import tqdm


"""
NOTES:

# iloc: Used to select data by position (integer-based indexing).
# loc: Used to select data by label (index-based selection). It’s often better for time series 
  where the index is a timestamp.

# idxmax and idxmin: Return the index (label) of the maximum and minimum values in a column.

# When using: df = df.loc[df_low.index[0]:, :]
  This line selects all rows in df starting from the first index of df_low.
  This ensures that the 'low' DataFrame contains all candlesticks relevant for the 'high' timeframe.
  It allows us to search for the local max and min for each candlestick in the lower timeframe.

# At the end, we use "None" in the column if we can't find a max or min value.
  This helps identify errors in the data, because by default the column contains NaNs.
  If we used "NaN" again, we couldn’t distinguish between missing data and data we intentionally marked as unresolved.
"""


def find_timestamp_extremum(df_high, df_low,save_path=""):
    """
    Parameters
    ----------
    df_high: pd.DataFrame who contains high timeframe
    df_low : pd.DataFrame who contains low timeframe
    save_path : path to save the file + "name.csv" (if you want to)

    Returns
    -------
    df_high with two new column (low_time and high_time)
    """
    #library
    import numpy as np
    import pandas as pd
    from tqdm import tqdm

    #copy the dataframe and synchronisation of our data frame
    df = df_high.copy()
    df = df.loc[df_low.index[0]:, :]

    #set new columns
    df["low_time"] = np.nan
    df["high_time"] = np.nan

    for i in tqdm(range(len(df)-1)):
        try:
            #Extract values from the lowest timeframe dataframe
            start = df.iloc[i:i+1, :].index[0]
            end = df.iloc[i+1:i+2, :].index[0]
            row_low = df_low.loc[start:end, :].iloc[:-1, :]

            #Extract Timestamp of the max and min over the period
            high = row_low["high"].idxmax()
            low = row_low["low"].idxmin()

            #Assign values to DataFrame
            df.loc[start, "high_time"] = high
            df.loc[start, "low_time"] = low

        except Exception as e:
            print(f"Erreur pour la période {start} - {end}: {e}")
            df.loc[start, "high_time"] = None
            df.loc[start, "low_time"] = None

    #verify the number of row without both TP and SL on same time
    percentage_good_row = len( df.dropna())/len(df)*100
    percentage_garbage_row = 100-percentage_good_row

    if percentage_garbage_row > 5:
        print(f"WARNINGS: Garbage row: {'%.2f' % percentage_garbage_row} %")
    else :
        print(f"We have {'%.2f'% percentage_good_row} % of Good Row" )

    col_high_low = ["high_time", "low_time"]
    print(df[col_high_low].head())

    #Save the file
    try :
        if len(save_path)>0:
            df.to_csv(save_path)
            print(f"✅ file save: {save_path}")

    except Exception as e:
     print(f"⚠️Warning :error to save the fil : {e}")



    return df

"""

#-------------

import os
path_low =????
path_high =????
save_path = ????

for path in [path_low, path_high,save_path]:
    if not os.path.exists(path):
        print(f"⚠️ Attention : Le fichier n'existe pas : {path}")
    else:
        print(f"✅ Fichier trouvé : {path}")



#exemple d'implementation

try:

    df_low_tf = pd.read_csv(path_low, index_col="time", parse_dates=True)
    df_high_tf = pd.read_csv(path_high, index_col="time", parse_dates=True)

    df = find_timestamp_extremum(df_high_tf, df_low_tf)

except Exception as e:
    print(f"⚠️ Attention : {e}")


df.head()

#------------

"""







"""

RÉCAPITULATIF DE LA FONCTION EN ÉTAPES SIMPLES (sans code)
But :
Pour chaque bougie du timeframe élevé (ex. 4H), on veut savoir à quelle minute exacte (dans les M1/M30) sont apparus :

le plus haut (high)

le plus bas (low)

🔹 Étape 1 : Synchronisation des données
On coupe le grand timeframe (df) pour qu’il commence au même moment que le petit timeframe (df_lower_timeframe).
Ça évite de travailler sur des périodes non alignées et ainsi nous somme sur que pour chaque bougie du grand timeframe
,on aura toutes les données du petit timeframe.

🔹 Étape 2 : Préparer deux colonnes vides
On crée deux nouvelles colonnes dans le grand timeframe :

high_time → l’heure précise du plus haut

low_time → l’heure précise du plus bas

🔹 Étape 3 : Pour chaque bougie du grand timeframe (sauf la dernière)
On boucle sur chaque intervalle du grand UT (par exemple 4h), et on fait :

On récupère le début (start) et la fin (end) de l’intervalle 4H actuel.

On prend toutes les bougies du petit timeframe comprises entre start et end (sans inclure end).

On cherche :

quelle minute a le plus haut prix → high_time

quelle minute a le plus bas prix → low_time

On note ces deux timestamps dans le grand timeframe, à la ligne correspondante.

🔹 Étape 4 : Gestion des erreurs
S’il y a un souci (données manquantes, etc.), on enregistre juste des valeurs vides et on affiche un message.

🔹 Étape 5 : Nettoyage
On enlève la dernière ligne (elle est incomplète, car elle n'a pas de end)
On affiche un pourcentage de lignes valides (informel).
"""