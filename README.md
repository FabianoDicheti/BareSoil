Para executar o experimento, navegue até o diretório “/bare” e execute os seguintes comandos:

sudo docker build -t bare .
sudo docker run --rm -v $(pwd)/static:/app/static bare


Após a execução, o projeto replicará o experimento. 

Ele fará o download das imagens dos arquivos KML localizados na pasta “/bare/kmlFiles”. Essas imagens serão utilizadas tanto para a aplicação do algoritmo EBSE proposto quanto para o método tradicional de índices intervalares.

Todos os valores calculados serão exibidos na tela com referências aos nomes dos arquivos KML correspondentes. As imagens serão armazenadas no diretório “/bare/static”.
