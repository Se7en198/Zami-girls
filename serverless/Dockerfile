# Imagen oficial de RunPod con ComfyUI preinstalado
FROM runpod/worker-comfyui:latest

# Copiar handler y script de inicio
COPY handler.py /handler.py
COPY start.sh   /start.sh

RUN pip install --no-cache-dir runpod requests && \
    chmod +x /start.sh

CMD ["/start.sh"]
