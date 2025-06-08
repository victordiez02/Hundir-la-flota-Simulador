# Resultados de 50,000 simulaciones por estrategia

## Resumen detallado por enfrentamiento

| Jugador 0   | Jugador 1   | J0 gana | J1 gana | % J0   | % J1   | Turnos | Duración | Precisión J0 | Precisión J1 | Disparos J0 | Disparos J1 |
| ----------- | ----------- | ------- | ------- | ------ | ------ | ------ | -------- | ------------ | ------------ | ----------- | ----------- |
| aleatoria   | aleatoria   | 25611   | 24389   | 51.2%  | 48.8%  | 735.5  | 0.01s    | 4.2%         | 4.2%         | 368.0       | 367.5       |
| aleatoria   | optimizada  | 420     | 49580   | 0.8%   | 99.2%  | 423.5  | 0.00s    | 4.3%         | 7.6%         | 211.8       | 211.7       |
| aleatoria   | optimizada2 | 1       | 49999   | 0.0%   | 100.0% | 309.3  | 0.00s    | 4.2%         | 10.3%        | 154.6       | 154.6       |
| optimizada  | aleatoria   | 49534   | 466     | 99.1%  | 0.9%   | 424.1  | 0.00s    | 7.5%         | 4.2%         | 212.5       | 211.5       |
| optimizada  | optimizada  | 24924   | 25076   | 49.8%  | 50.2%  | 347.3  | 0.00s    | 8.2%         | 8.2%         | 173.9       | 173.4       |
| optimizada  | optimizada2 | 12015   | 37985   | 24.0%  | 76.0%  | 291.0  | 0.00s    | 8.9%         | 10.4%        | 145.6       | 145.4       |
| optimizada2 | aleatoria   | 50000   | 0       | 100.0% | 0.0%   | 307.7  | 0.00s    | 10.4%        | 4.2%         | 154.3       | 153.3       |
| optimizada2 | optimizada  | 38364   | 11636   | 76.7%  | 23.3%  | 290.1  | 0.00s    | 10.4%        | 8.9%         | 145.4       | 144.7       |
| optimizada2 | optimizada2 | 25350   | 24650   | 50.7%  | 49.3%  | 272.5  | 0.00s    | 10.5%        | 10.5%        | 136.5       | 136.0       |

---

## Porcentaje de victorias del Jugador 1

| J0 \ J1         | aleatoria | optimizada | optimizada2 |
| --------------- | --------- | ---------- | ----------- |
| **aleatoria**   | 48.8%     | 99.2%      | 100.0%      |
| **optimizada**  | 0.9%      | 50.2%      | 76.0%       |
| **optimizada2** | 0.0%      | 23.3%      | 49.3%       |
