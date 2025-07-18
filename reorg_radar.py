#!/usr/bin/env python3
"""
ReorgRadar — мониторинг цепных реорганизаций (reorg) на Ethereum.
При обнаружении reorg логирует предупреждение и детали.
"""

import os
import time
import logging
from web3 import Web3

# --- Настройки ---
RPC_URL       = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))  # секунды

# Настройка логирования
logging.basicConfig(
    filename=os.getenv("LOG_FILE", "reorg_radar.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
logging.getLogger().addHandler(console)

def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        logging.error("Не удалось подключиться к RPC‑узлу: %s", RPC_URL)
        return

    logging.info("🔍 ReorgRadar запущен, опрос каждые %s сек.", POLL_INTERVAL)
    last_block = w3.eth.block_number
    last_hash  = w3.eth.get_block(last_block).hash.hex()
    logging.info("Стартовый блок: #%d (%s)", last_block, last_hash)

    while True:
        try:
            current = w3.eth.block_number
            # если появились новые блоки
            if current > last_block:
                for bn in range(last_block + 1, current + 1):
                    blk = w3.eth.get_block(bn)
                    # проверяем parentHash
                    if blk.parentHash.hex() != last_hash:
                        logging.warning(
                            "⚠️ Reorg! Блок #%d имеет parentHash %s, ожидаемый %s",
                            bn, blk.parentHash.hex(), last_hash
                        )
                    else:
                        logging.info("Блок #%d подтверждён (hash=%s)", bn, blk.hash.hex())
                    # обновляем last
                    last_hash  = blk.hash.hex()
                    last_block = bn
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            logging.info("Выход по Ctrl-C")
            break
        except Exception as e:
            logging.error("Ошибка: %s", e)
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
