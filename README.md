# **Agentic Pharma Sales Force Automation System**

A complete **Pharma Sales Force Automation (SFA) Agentic System** designed for pharmaceutical field operations.
This project integrates **agentic workflows, intelligent planning, route optimization, RCPA logging, physician visit capture, and a Streamlit dashboard** — all built using Python and multi-agent reasoning.

## **1. Problem Statement**

Pharmaceutical companies rely heavily on Medical Representatives (MRs) for:

* Physician visits
* Product detailing
* RCPA (Retail Chemist Prescription Audit)
* Competitor tracking
* Prescription generation

However, most field workflows are still **manual**, causing:

* Inefficient doctor segmentation
* Poor MR scheduling
* Redundant routes & long travel times
* Lack of personalized detailing
* Missing or unstructured MR notes
* Scattered RCPA insights
* No real-time manager visibility

Enterprise SFA systems exist but are expensive.
This project builds a **cost-free, intelligent, agent-powered SFA system** from scratch.

## **2. Why Agents?**

Pharma workflows require:

* Segmentation
* Reasoning
* Planning
* Travel estimation
* Memory
* Multi-step tool use
* Document generation
* Dashboard sync

These are ideal for agentic systems.

### **Agents here perform:**

* Task decomposition
* Intelligent reasoning
* CSV/JSON read–write
* Multi-step planning
* Map generation
* Streamlit UI updates

## **3. System Architecture**

This project has five major components:

## **A. Synthetic Data Generator**

Generates realistic pharma datasets:

* Doctors
* Hospitals
* MR representatives
* Past visits
* RCPA chemist audits

Outputs:

```
doctors_master.csv
hospitals_master.csv
mr_reps.csv
physician_visit_table.csv
rcpa_chemist_table.csv
```

## **B. Intelligence Agent (Segmentation + Molecule Strategy)**

* Doctor segmentation: **High / Medium / Low**
* Molecule suggestion per therapy area

Output:
`doctors_segmented.csv`

---

## **C. Planner Agent (Core Engine)**

Creates a **7-day intelligent MR visit plan**:

* MR → Doctor assignment
* Daily slots
* Travel distance & time
* Call duration
* Molecule recommendations
* Optimized route
* Folium travel map

Outputs:
```
next_7day_mr_visit.csv
next_7day_mr_visit_full.json
pair_travel_estimates.csv
plan_metrics.json
mr_travel_map.html
```

## **D. Dashboard & Visualization Agent**

Generates automatically:

* KPIs & statistics
* Segment-wise doctor coverage
* MR workload
* Therapy area analysis
* Travel map

## **E. Streamlit Front-End Agent**

An interactive SFA dashboard with:

### **1. Weekly MR Visit Planner**

* Filters (MR, segment, therapy, date)
* Search
* KPIs
* Export options
* Embedded travel map

### **2. MR Notes Editor**

* In-place editing
* Timestamp tracking
* User tracking
* Safe write with backups

### **3. Physician Visit Form**

Writes to `physician_visit_table.csv`:

* Doctor visit logs
* Samples given
* Products detailed
* Objections
* Rx commitment
* Photo proof

### **4. RCPA Chemist Audit Form**

Writes to `rcpa_chemist_table.csv`:

* Competitor brands
* Weekly demand
* MRP comparison
* Margin analysis
* Stock availability
* Photo proof

Everything updates **in real-time**.

# **4. How to Run**

### **Run Notebook Pipeline**

Execute all cells in `pipeline.ipynb`:

1. Generate synthetic data
2. Segment doctors
3. Assign molecules
4. Build 7-day MR plan
5. Compute travel
6. Build map
7. Generate all output files

### ** Run Streamlit Dashboard**

```bash
streamlit run streamlit_app.py
```

This opens a full-feature SFA dashboard.

# **5. Technologies & Tools Used**

### **Core Libraries**

* pandas
* numpy
* haversine
* uuid

### **Visualization**

* folium
* matplotlib

### **Interface**

* Streamlit

### **Agent Skills**

* Multi-step reasoning
* Tool use
* File operations
* Travel computation
* Dynamic form creation
* Map embedding

# **6. Project Outputs**

A fully functional SFA system that produces:

* Doctor segmentation
* Weekly MR visit plan
* Travel map
* RCPA chemist table
* Physician visit table
* MR-level summaries
* Dashboard & UI
* Metrics JSON/CSV

# **7. Future Enhancements**

* Google Maps API integration
* Predictive prescription forecasting
* Territory rebalancing
* Role-based access (MR, Manager, Admin)
* Cloud deployment (Streamlit Cloud, Render, GCP)
* Voice-based MR note-taking
* Notification engine

# **8. Conclusion**

This project demonstrates a complete **Agentic Pharma Sales Force Automation System**, showcasing:

* Intelligent decision-making
* Travel optimization
* Multi-agent coordination
* Real-time data collection
* Dashboard-driven insights

A fully functioning, end-to-end SFA platform—built entirely with Python and agentic automation.
