# Fundamentals-of-Digitals-Project

 # Shopee Group-Buy Price Calculator

> A small project that explains how small vendors moved from traditional markets to digital storefronts (Shopee case study) and includes an interactive group-buy price calculator.

---

## 📖 Project Overview

This repository contains:

* A **case study** on the vendor journey from offline to online (using Shopee).
* A **Python interactive program** to calculate prices, revenue, and savings for group-buy scenarios.

---

## 🏪 Vendor Journey Summary

| Stage | Description                                                                                       |
| ----- | ------------------------------------------------------------------------------------------------- |
| 1     | Vendors relied on *pasar malam* and local *kedai runcit* with limited exposure.                   |
| 2     | Lazada/eBay were available but costly and not micro-vendor-friendly.                              |
| 3     | Shopee launched a free-to-join, mobile-first platform with free shipping vouchers.                |
| 4     | Thousands joined during MCO (COVID-19), causing huge growth.                                      |
| 5     | Customer buying habits shifted online; competitors copied Shopee's model.                         |
| 6     | Vendors now use a hybrid (offline + online) model. Customers expect online discounts as the norm. |

### Clayton Christensen’s Disruptive Innovation Model

Shopee disrupted the market by providing a simpler, cheaper, and accessible solution for micro-sellers. Over time, it attracted mainstream users and forced competitors to adapt.

---

## ✨ Features

✅ Calculate price per person (with or without discount)
✅ Compute total revenue seller will earn
✅ Show savings per person when discount applies
✅ Clean, simple CLI design

---

## 🧮 Inputs & Outputs

**Inputs:**

* Product Name
* Original Price (per item)
* Group Size (number of buyers)
* Discount Rate (% applied if group size ≥ threshold)
* Minimum Required Group Size (threshold to activate discount)

**Outputs:**

* Price per person (discounted if applicable)
* Total revenue
* Savings per person (if discount applied)

---

## 🖥 Installation & Usage

Clone the repo and run the program:

```bash
git clone https://github.com/<your-username>/shopee-groupbuy-calculator.git
cd shopee-groupbuy-calculator
python groupbuy.py
```

Follow the prompts and enter the required values.

---

## 🧠 Example Run

**Input:**

* Product: Reusable Water Bottle
* Original Price: RM 25.00
* Group Size: 6
* Discount Rate: 20%
* Minimum Required: 5

**Output:**

* Discounted Price: RM 20.00 per person
* Total Revenue: RM 120.00
* Savings Per Person: RM 5.00

---

## 🤝 Contributing

Pull requests are welcome. Ideas:

* Add a web/GUI version
* Import/export CSV for multiple products
* Add automated tests

---

## 📜 License

MIT License. See `LICENSE` for details.
