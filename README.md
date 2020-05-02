# LazyRolls Home Assistant plugin

Automatic motorized roller blinds project. Home Assistant plugin

Моторизированный привод для рулонных штор(http://imlazy.ru/). Плагин для Home Assistant

## Config
```
  - platform: lazyrolls
    covers:
      bedroom_l:
        friendly_name: "Bedroom left"
        ip_address: "192.168.117.31"
      bedroom_r:
        friendly_name: "Bedroom right"
        ip_address: "192.168.117.32"
```

### Ссылки / Links
Описание проекта / main project: [https://github.com/ACE1046/LazyRolls](https://github.com/ACE1046/LazyRolls)

### Установка / Install
You can install this customization via [https://hacs.xyz/](HACS), just add current repo url as an additional source on the setting of HACS

### TODO:
- Add config flow support

### Changelog
-02.05.2020 v0.02 beta\
Управление положением, обновление статуса

-30.04.2020 v0.01 beta\
Первая пробная версия
