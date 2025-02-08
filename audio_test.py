import torch
import numpy
import librosa
import torchaudio

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#model.to(device)

