import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
import sys
import warnings
warnings.filterwarnings('ignore')

# Função para prever o nível de ruído (Sound Pressure Level) com dados específicos
def prever_ruido(frequency, suction_thickness, chord_length, angle_of_attack, free_stream_velocity):
    # Carregar o modelo salvo em pickle
    with open('aerofolio_rf_model_499_best.pkl', 'rb') as file:
        modelo = pickle.load(file)
    
    # Carregar os dados de aerofólio (usado para manter a consistência da normalização)
    dados = pd.read_csv('aerofolio_data.csv')
    
    # Normalizar os dados (usar o mesmo scaler usado no treinamento)
    scaler = StandardScaler()
    features = ['Frequency', 'Suction_Thickness', 'Chord_Length', 'Angle_of_Attack', 'Free_Stream_Velocity']
    #return (dados[features].head())
    dados[features] = scaler.fit_transform(dados[features])
    
    # Criar DataFrame para os dados fornecidos
    dados_fornecidos = pd.DataFrame({
        'Frequency': [frequency],
        'Suction_Thickness': [suction_thickness],
        'Chord_Length': [chord_length],
        'Angle_of_Attack': [angle_of_attack],
        'Free_Stream_Velocity': [free_stream_velocity]
    })
    
    # Normalizar os dados fornecidos da mesma forma
    dados_fornecidos[features] = scaler.transform(dados_fornecidos[features])
    
    # Prever o nível de ruído
    ruido_estimado = modelo.predict(dados_fornecidos)
    
    #print(f"Ruído estimado: {ruido_estimado[0].round(2)} dB")
    
    return ruido_estimado[0].round(2)

if __name__ == "__main__":
    # Coletar os parâmetros de entrada via linha de comando
    frequency = 3000
    suction_thickness = 1.8
    chord_length = 0.28
    angle_of_attack = 60
    free_stream_velocity = 0.002
    

    # Prever o nível de ruído com os parâmetros fornecidos
    ruido_estimado = prever_ruido(frequency, suction_thickness, chord_length, angle_of_attack, free_stream_velocity)
    
