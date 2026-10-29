// Weergave-onderdelen: ze tonen de spelstatus, maar bevatten geen spellogica.

import { COLOR_LABELS } from "./config.js";

const money = new Intl.NumberFormat("nl-NL", { style: "currency", currency: "EUR" });

export const formatMoney = (amount) => money.format(amount);

export function formatSigned(amount) {
  const sign = amount > 0 ? "+" : amount < 0 ? "−" : "";
  return sign + money.format(Math.abs(amount));
}

export function formatTime(date) {
  return date.toLocaleTimeString("nl-NL", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function setTone(element, amount) {
  element.classList.toggle("positive", amount > 0);
  element.classList.toggle("negative", amount < 0);
}

export class StatsView {
  constructor() {
    this.el = {
      balance: document.getElementById("stat-balance"),
      won: document.getElementById("stat-won"),
      lost: document.getElementById("stat-lost"),
      net: document.getElementById("stat-net"),
      upkeep: document.getElementById("stat-upkeep"),
      upkeepNote: document.getElementById("stat-upkeep-note"),
      bots: document.getElementById("stat-bots"),
      botsNote: document.getElementById("stat-bots-note"),
    };
  }

  render(state) {
    this.el.balance.textContent = formatMoney(state.balance);
    this.el.balance.classList.toggle("negative", state.balance < 0);
    this.el.won.textContent = formatMoney(state.total_won);
    this.el.lost.textContent = formatMoney(state.total_lost);
    this.el.net.textContent = formatSigned(state.net_profit);
    setTone(this.el.net, state.net_profit);
    this.el.upkeep.textContent = `${formatMoney(state.upkeep_per_round)} per ronde`;
    this.el.upkeepNote.textContent = `${formatMoney(state.upkeep_per_spin)} per botspin`;
    this.el.bots.textContent = String(state.bots.active);
    this.el.botsNote.textContent = state.bots.active > 0
      ? `spelen elke ${state.bots.interval_seconds} s`
      : "nog geen bots";
  }
}

export class ShopView {
  constructor(list, onBuy) {
    this.list = list;
    this.onBuy = onBuy;
    this.items = new Map();
  }

  render(upgrades, balance) {
    for (const upgrade of upgrades) {
      let item = this.items.get(upgrade.id);
      if (!item) {
        item = this.createItem(upgrade.id);
        this.items.set(upgrade.id, item);
        this.list.append(item.root);
      }

      const maxed = upgrade.max_level != null && upgrade.level >= upgrade.max_level;
      item.name.textContent = upgrade.name;
      item.description.textContent = upgrade.description;
      item.level.textContent = upgrade.max_level != null
        ? `Niveau ${upgrade.level} / ${upgrade.max_level}`
        : `Niveau ${upgrade.level}`;
      item.button.textContent = maxed ? "Maximaal" : formatMoney(upgrade.price);
      item.button.disabled = maxed || balance < upgrade.price;
      item.button.setAttribute(
        "aria-label",
        maxed ? `${upgrade.name} is maximaal` : `Koop ${upgrade.name} voor ${formatMoney(upgrade.price)}`,
      );
    }
  }

  createItem(id) {
    const root = document.createElement("li");
    root.className = "upgrade";
    root.innerHTML = `
      <div class="upgrade-info">
        <div class="upgrade-head"><h3 class="upgrade-name"></h3><span class="upgrade-level"></span></div>
        <p class="upgrade-description"></p>
      </div>
      <button type="button" class="btn btn-gold upgrade-buy"></button>`;

    const button = root.querySelector(".upgrade-buy");
    button.addEventListener("click", () => {
      button.disabled = true;
      this.onBuy(id);
    });

    return {
      root,
      button,
      name: root.querySelector(".upgrade-name"),
      level: root.querySelector(".upgrade-level"),
      description: root.querySelector(".upgrade-description"),
    };
  }
}

export class HistoryView {
  constructor(list) {
    this.list = list;
    this.lastKey = "";
  }

  render(history) {
    const key = JSON.stringify(history);
    if (key === this.lastKey) return;
    this.lastKey = key;

    if (history.length === 0) {
      const empty = document.createElement("li");
      empty.className = "history-empty";
      empty.textContent = "Nog geen spins gespeeld.";
      this.list.replaceChildren(empty);
      return;
    }

    this.list.replaceChildren(...history.map((spin) => {
      const li = document.createElement("li");
      li.className = "history-item";
      li.innerHTML = `
        <span class="pocket pocket-${spin.color}"></span>
        <span class="history-source"></span>
        <span class="history-net"></span>`;
      li.querySelector(".pocket").textContent = spin.number;
      li.querySelector(".history-source").textContent = spin.source === "bot" ? "Bot" : "Jij";
      const net = li.querySelector(".history-net");
      net.textContent = formatSigned(spin.net);
      setTone(net, spin.net);
      return li;
    }));
  }
}

export class ResultView {
  constructor(root) {
    this.number = root.querySelector(".result-number");
    this.text = root.querySelector(".result-text");
    this.last = null;
  }

  show(result) {
    this.last = result;
    if (!result) {
      this.number.textContent = "–";
      this.number.className = "result-number";
      this.text.textContent = "Plaats een inzet en draai aan het wiel.";
      this.text.className = "result-text";
      return;
    }
    this.number.textContent = result.number;
    this.number.className = `result-number pocket-${result.color}`;
    const outcome = result.net > 0
      ? `Je wint ${formatMoney(result.net)}`
      : `Je verliest ${formatMoney(Math.abs(result.net))}`;
    this.text.textContent = `${result.number} ${COLOR_LABELS[result.color]}: ${outcome}`;
    this.text.className = `result-text ${result.net > 0 ? "positive" : "negative"}`;
  }

  showSpinning() {
    this.number.textContent = "…";
    this.number.className = "result-number";
    this.text.textContent = "Het wiel draait…";
    this.text.className = "result-text";
  }

  restore() {
    this.show(this.last);
  }
}

export class Toast {
  constructor(root) {
    this.root = root;
    this.timer = null;
  }

  show(message, kind = "info") {
    this.root.textContent = message;
    this.root.className = `toast toast-${kind} visible`;
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.root.classList.remove("visible"), 3500);
  }
}
