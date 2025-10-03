#!/bin/bash

# Nome da impressora
IMPRESSORA="VersaLink_C7020_S25"
SERVIDOR="localhost:631"

# Verifica se o arquivo foi passado
if [ -z "$1" ]; then
    echo "Uso: $0 <arquivo>"
    exit 1
fi

ARQUIVO="$1"

# Verifica se o arquivo existe
if [ ! -f "$ARQUIVO" ]; then
    echo "Erro: Arquivo '$ARQUIVO' não encontrado!"
    exit 1
fi

# Detecta o tipo do arquivo
TIPO=$(file --mime-type -b "$ARQUIVO")

echo "Enviando '$ARQUIVO' para impressão..."
echo "Tipo detectado: $TIPO"

# Envia para a impressora
lp -d "$IMPRESSORA" -h "$SERVIDOR" "$ARQUIVO"

# Confirmação
if [ $? -eq 0 ]; then
    echo "Impressão enviada com sucesso!"
else
    echo "Falha ao enviar para impressão."
    exit 1
fi

