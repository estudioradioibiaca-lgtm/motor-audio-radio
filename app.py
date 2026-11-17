import os
import zipfile
from flask import Flask, request, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/baixar', methods=['POST'])
def baixar_musicas():
    data = request.json
    lista_musicas = data.get('musicas', [])

    output_dir = '/tmp/downloads'
    os.makedirs(output_dir, exist_ok=True)

    baixados = []
    for musica in lista_musicas:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'noplaylist': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                query = f"ytsearch1:{musica}"
                info = ydl.extract_info(query, download=True)
                if 'entries' in info:
                    info = info['entries'][0]

                mp3_filename = os.path.join(output_dir, f"{info['id']}.mp3")
                final_name = os.path.join(output_dir, f"{musica}.mp3".replace('/', '-'))

                if os.path.exists(mp3_filename):
                    os.rename(mp3_filename, final_name)
                    baixados.append(final_name)
        except Exception as e:
            print(f"Erro ao baixar {musica}: {e}")

    zip_path = '/tmp/musicas_radio.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in baixados:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))

    return send_file(zip_path, as_attachment=True, download_name='pacote_musicas.zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
