# Chuguan Home

[![Release][releaseBadge]][releaseUrl]

---

**Chuguan Home** is a Home Assistant custom integration for smart home devices from **Chuguan (初冠)** and **Xiao Zhihui (小智慧)**.

It allows you to connect your smart home account to Home Assistant, discover devices in your selected home, and control supported devices directly from Home Assistant.


## 🚀 Get Started in Minutes!


### 1. Install ChuGuan Home

[![Open in HACS at your Home Assistant instance.][hacsBadge]][ChuGuanStrategyHacs]

### 2. Manual Installation

1. Download the latest release from [GitHub Releases][releaseUrl].
2. Extract the `chuguan_home` directory.
3. Copy it into your Home Assistant configuration directory:

    ```text
    config/
    └── custom_components/
        └── chuguan_home/
            ├── __init__.py
            ├── config_flow.py
            ├── manifest.json
            └── ...
    ```

4. Restart Home Assistant.


## Configuration

1. Open **Settings → Devices & Services**.
2. Click **Add Integration**.
3. Search for **Chuguan Home**.
4. Select your smart home brand:
   - Chuguan (初冠)
   - Xiao Zhihui (小智慧)
5. Enter your smart home account and password.
6. Select the home you want to connect.
7. Complete the setup.

After setup, the integration will automatically discover supported devices in the selected home and create the corresponding Home Assistant entities.

## Supported Brands

| Brand | Description |
|---|---|
| [初冠 (Chuguan)](https://chuguansmart.com/download.html) | Chuguan smart home devices |
| [小智慧 (Xiao Zhihui)](https://xiaozhihui.vip/downloadxzh.html) | Xiao Zhihui smart home devices |


## Supported Devices

The integration supports the following device categories, depending on the device model and the capabilities exposed by the vendor platform.

| Device Type | Home Assistant Entity | Description |
|---|---|---|
| Switches | Switch | Turn devices on and off |
| Lights | Light | Control light power and supported lighting features |
| Smart Plugs | Switch | Control smart plug power |
| Curtains / Windows | Cover | Open, close, and control curtain position where supported |
| Air Conditioners | Climate | Control operating mode and supported temperature settings |
| Bathroom Heaters | Switch / Light | Control supported heating, ventilation, and lighting functions |
| Clothes Drying Racks | Cover / Switch / Light / Button | Control supported lifting and other functions |
| Cameras | Camera | View camera streams and use supported camera controls |
| Mechanical hand | Valve | Open close and stop the mechanical hand |
   


## Camera PTZ Service

The integration provides the `chuguan_home.camera_ptz` service for controlling supported camera movement.

### Service

```yaml
action: chuguan_home.camera_ptz
data:
  entity_id: camera.your_camera
  direction: 0
  speed: 0
```

### Parameters

| Parameter | Description |
|---|---|
| `entity_id` | The camera entity to control |
| `direction` | The PTZ movement direction |
| `speed` | The PTZ movement speed |

The `direction` and `speed` parameters use numeric values as listed below.

| Direction | Value |
|---|---|
| Up | 0 |
| Down | 1 |
| Left | 2 |
| Right | 3 |
| Left Up | 4 |
| Left Down | 5 |
| Right Up | 6 |
| Right Down | 7 |

| Speed | Value |
|---|---|
| Slow | 0 |
| Medium | 1 |
| Fast | 2 |


For example, the service can be used to move a compatible camera upward:

```yaml
action: chuguan_home.camera_ptz
data:
  entity_id: camera.your_camera
  direction: 0
  speed: 0
```

Replace `camera.your_camera` with your actual camera entity ID.



---

[hacsBadge]: https://my.home-assistant.io/badges/hacs_repository.svg


<!-- Badge References -->

[releaseBadge]: https://img.shields.io/github/v/tag/wang-chuanhui/chuguan_home?label=Release

<!-- Repository References -->

[releaseUrl]: https://github.com/wang-chuanhui/chuguan_home/releases/latest
[ChuGuanStrategyHacs]: https://my.home-assistant.io/redirect/hacs_repository/?owner=wang-chuanhui&repository=chuguan_home&category=integration
