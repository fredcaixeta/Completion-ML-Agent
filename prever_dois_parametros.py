import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def encontrar_menores_ruidos(range_frequency=None, range_suction_thickness=None, range_chord_length=None, 
                             range_angle_of_attack=None, range_free_stream_velocity=None):
    # Carregar os dados do aerofólio
    aerofolio_data = pd.read_csv('aerofolio_data.csv')

    # Carregar o modelo do arquivo Pickle
    with open('aerofolio_rf_model_500.pkl', 'rb') as file:
        modelo_carregado = pickle.load(file)

    # Definir os dois valores de entrada para cada parâmetro fornecido
    def gerar_combinacoes(range_val):
        if range_val is not None:
            return [range_val[0], range_val[1]]
        else:
            return None

    # Criar as combinações para cada parâmetro
    frequencies = gerar_combinacoes(range_frequency)
    suction_thicknesses = gerar_combinacoes(range_suction_thickness)
    chord_lengths = gerar_combinacoes(range_chord_length)
    angles_of_attack = gerar_combinacoes(range_angle_of_attack)
    free_stream_velocities = gerar_combinacoes(range_free_stream_velocity)

    # Criar uma lista para armazenar as combinações
    combinacoes = []

    # Para cada combinação de parâmetros gerados (2 valores por parâmetro fornecido)
    for frequency in (frequencies if frequencies is not None else [None]):
        for suction_thickness in (suction_thicknesses if suction_thicknesses is not None else [None]):
            for chord_length in (chord_lengths if chord_lengths is not None else [None]):
                for angle_of_attack in (angles_of_attack if angles_of_attack is not None else [None]):
                    for free_stream_velocity in (free_stream_velocities if free_stream_velocities is not None else [None]):
                        combinacoes.append([frequency, suction_thickness, chord_length, angle_of_attack, free_stream_velocity])

    # Remover combinações inválidas (onde todos os valores são None)
    combinacoes = [c for c in combinacoes if any(val is not None for val in c)]

    # Criar DataFrame com as combinações geradas
    df_combinacoes = pd.DataFrame(combinacoes, columns=['Frequency', 'Suction_Thickness', 'Chord_Length', 'Angle_of_Attack', 'Free_Stream_Velocity'])

    # Normalizar as features com o mesmo scaler usado no treinamento
    scaler = StandardScaler()
    features = ['Frequency', 'Suction_Thickness', 'Chord_Length', 'Angle_of_Attack', 'Free_Stream_Velocity']

    # Substituir valores None por valores médios dos dados de treino antes de normalizar
    for feature in features:
        if df_combinacoes[feature].isnull().any():
            media_valor = aerofolio_data[feature].mean()
            df_combinacoes[feature].fillna(media_valor, inplace=True)

    # Ajuste: guardar valores originais para reverter depois da normalização
    df_combinacoes_originais = df_combinacoes.copy()

    # Normalizar as combinações
    df_combinacoes[features] = scaler.fit_transform(df_combinacoes[features])

    # Fazer a predição do nível de ruído para as combinações
    df_combinacoes['Sound_Pressure_Level_Predito'] = modelo_carregado.predict(df_combinacoes[features])

    # Ordenar pelos menores valores de ruído predito
    menores_ruidos = df_combinacoes.sort_values(by='Sound_Pressure_Level_Predito').head(5)

    # Ajuste: voltar aos valores originais antes da normalização para exibir ao usuário
    menores_ruidos[features] = df_combinacoes_originais[features]

    # Exibir as 5 menores combinações de ruído predito com valores originais
    resultado = menores_ruidos[['Frequency', 'Suction_Thickness', 'Chord_Length', 'Angle_of_Attack', 'Free_Stream_Velocity', 'Sound_Pressure_Level_Predito']]
    
    return resultado

if __name__ == "__main__":
    # Exemplo de parâmetros para consulta com ranges fornecidos (dois valores por parâmetro)
    range_frequency = (1000, 2000)  # 1000 ou 2000
    range_suction_thickness = (1, 1.5)  # 1 ou 1.5
    range_chord_length = (0.28, 0.3)  # 0.28 ou 0.3
    range_angle_of_attack = (50, 60)  # 50 ou 60
    range_free_stream_velocity = (0.003, 0.005)  # 0.003 ou 0.005

    resultado = encontrar_menores_ruidos(range_frequency, range_suction_thickness, range_chord_length, range_angle_of_attack, range_free_stream_velocity)
    print(resultado)
