from django.shortcuts import render
from .forms import AudioForm
from .processingAudio import Amplitude,spectogram,silence
    # ,emotionOutput

def home(request):
    if request.method == 'POST':
        form = AudioForm(request.POST,request.FILES)
        if form.is_valid():
            audio_name = form.cleaned_data['audio']
            # ans = emotionOutput(audio_name)
            # out = ans.split('_')
            context = {
                'amp': Amplitude(audio_name),
                'sep': spectogram(audio_name),
                'sil': silence(audio_name),
                # 'gen' : out[0],
                # 'emo' : out[1],
            }
            return render(request, 'audio/out.html', context)

    else:
        form = AudioForm()

    return render(request, 'audio/main.html', {'form': form})


def test(request):
    return render(request,'base.html')
