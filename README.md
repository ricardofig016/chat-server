# Servidor de Chat em Python

## Descrição

Trabalho desenvolvido em Python de um **servidor de chat** e de um **cliente** simples para comunicar com ele. O servidor baseia-se no modelo **multiplex**. O cliente usa **duas threads**, de modo a poder receber mensagens do servidor enquanto espera que o utilizador escreva a próxima **mensagem** ou **comando**.

## Como utilizar

### Iniciar o servidor

```shell
python3 chat_server.py [port_number]
```

```shell
python3 chat_server.py 7777
```

### Iniciar o cliente

```shell
python3 chat_client.py
```

## Comandos do Cliente

- **/nick _name_** : escolher um nome ou mudar de nome.
- **/join _room_** : entrar numa sala de chat ou para mudar de sala.
- **/leave** : sair da sala de chat.
- **/bye** : desligar o cliente.
