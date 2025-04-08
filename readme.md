# <center> SLEEP GUARD: Detecção de fadiga com Visão Computacional e acionamento de alarme </center>
<br></br>
### Utiliza MediaPipe, OpenCV, e Arduino para detectar sinais de sonolência e fadiga em tempo real, com base em movimentos faciais como piscadas, bocejos e quedas de cabeça para selecionar alarme 🚨
##

### 👁 Piscadas (EAR - Eye Aspect Ratio)
- `BLINK_THRESH = 0.45`: Threshold de olho fechado (limiares testados 25, 38, 45 e 50)
- `TIME_WINDOW = 15`: Janela de tempo (em segundos) pra contagem as piscadas frequentes
- `BLINK_COUNT_THRESH = 10`: Número de piscadas considerado fadiga (de acordo também com limiar da janela de tempo)

### 😮 Bocejos (MAR - Mouth Aspect Ratio)
- `YAWN_THRESH = 0.7`: Threshold para considerar bocejo
- `YAWNING_BLINKS = 8`: Quantidade de piscadas com bocejo
- `CONTROL_ALERT = 5`: Intervalo (em segundos) entre acionar alertas consecultivos
- `FREEZE = 10`: "congelar" o acionamento do alarme para não acionar beeps consecultivos logo após o acionamento de alerme

### 🙂‍↕️ Queda de Cabeça (posição vertical do nariz)
- `TRESH_NOSE_Y = 400`: considerando vertical (como ponto Y) - Quanto menor, mais sensível à queda; Quanto maior, menos sensível
- `INSTERVAL_FALLS = 1`: Intervalo (em segunos) entre cada queda de cabeça
- `THRESHOLD_FALLS = 2`: Número de quedas de cabeça por intervalo (INTERVAL_FALLS)

### 😴 Sonolência (olhos fechados por tempo prolongado)
- `START_THRESH = 0.50`: Limiar pra indicar olho fechado (Limiares testados 25, 38, 45 e 50)
- `CLOSED_TIME_THRESH = 5`: Tempo (em segundos) para indicar olho fechado

##
- `main.py`: Processa vídeo e chama os módulos para verificação de fadiga/sonolência.
- `alerta_fadiga.py`: Detecta fadiga com base em piscadas, bocejos e quedas de cabeça.
- `alerta_sonolencia.py`: Detecta sonolência por olhos fechados prolongadamente.

### 🪑 Usabilidade
- `USE_ARDUINO`: Ativa o acionamento de alarme com Arduino. (Use False, se não houver Arduino conectado)

## ⚠️ Requisitos

- Python 3.x
- OpenCV
- MediaPipe
- NumPy

obs:. (consulte requirements.txt para mais informações)
>  Arduino:
- Arduino com conexão serial (USB)
- Módulo de Buzzer ativo
- 3 jumpers machos

## 📝 Observações
- Os limiares podem ser ajustados conforme necessidade
- Ao executar sem usar o arduino, `USE_ARDUINO` deve ser `False`