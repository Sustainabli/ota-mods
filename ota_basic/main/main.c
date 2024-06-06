#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_http_client.h"
#include "esp_https_ota.h"
#include "esp_wifi.h"
#include "wifi_credentials.h"
#include "sdkconfig.h"


static const char *TAG = "OTA_UPDATE";

// Function declarations
void wifi_init(void);
static void ota_task(void *pvParameter);

void app_main(void) {
    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Initialize the WiFi
    wifi_init();

    // Start the OTA task
    xTaskCreate(&ota_task, "ota_update_task", 8192, NULL, 5, NULL);
}

void wifi_init(void) {
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = EXAMPLE_ESP_WIFI_SSID,
            .password = EXAMPLE_ESP_WIFI_PASS,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
        },
    };

    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config);
    esp_wifi_start();
}

static void ota_task(void *pvParameter) {
    ESP_LOGI(TAG, "Starting OTA update...");

    esp_http_client_config_t ota_config = {
        .url = "http://example.com/firmware.bin",
        .cert_pem = NULL,  // If your server uses HTTPS, set this to the server's root CA certificate.
    };

    // Start OTA update
    esp_err_t result = esp_https_ota(&ota_config);
    if (result == ESP_OK) {
        ESP_LOGI(TAG, "OTA Update Completed. Rebooting...");
        esp_restart();
    } else {
        ESP_LOGE(TAG, "OTA Update Failed");
    }
}
