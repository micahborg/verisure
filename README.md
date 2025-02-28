# **VerifiSure**

### **AI & ZK-Powered AVS for Insurance Claims Validation**

## **Context & Problem Statement**

**For many patients, insurance claim delays aren’t just frustrating—they’re life-threatening.** People facing urgent medical conditions, including terminal illnesses, are often left in limbo, unsure whether they can afford life-saving treatments while waiting for insurers to process claims. These long wait times create **immense emotional, physical, and financial stress**, forcing patients and families into impossible choices.

Meanwhile, insurance companies face exploitation by bad actors looking to abuse the system with fraudulent claims, increasing the burden on the patient with tighter restrictions and increased insurance premiums. These increases make healthcare more out of reach for the average person.

The result? A vicious cycle where **trust erodes, costs rise, and patients suffer.**

## By the numbers

- 75% of those who experienced coverage denials reported **delays in care**, and 47% of patients who faced coverage denials indicated that their health conditions deteriorated as a result. (https://www.ajmc.com/view/survey-exposes-pervasive-billing-errors-aggressive-tactics-in-us-health-insurance)
- 54% of patients reported that health insurance was **too expensive** as part of their family budget, had difficulty affording insurance, or both. (https://www.aha.org/news/perspective/2023-07-14-lets-end-commercial-insurer-barriers-reduce-access-care)
- Healthcare fraud and abuse combined cost the U.S. an estimated **$308 billion annually**.(https://www.forbes.com/advisor/insurance/fraud-statistics/)
- In a survey of 1,000 doctors, 30% said they waited at least three business days on average for a prior authorization decision from health plans (https://www.ama-assn.org/practice-management/prior-authorization/how-insurance-companies-red-tape-can-delay-patient-care).

## Medical Claims: A Timeline

When you schedule a visit to a healthcare provider, they will normally ask you for at least 3 things:

- Your Name
- Your Date of Birth
- Your Insurance Information

This information is necessary to begin the Revenue Cycle. But how do these providers manage patient data, insurance claims, and billing all at the some time?

### Medical Claims Clearinghouse

A clearinghouse is an agency that collects and distributes information. In the medical claims setting, this type of clearinghouse assists healthcare providers in processing patient insurance claims and billing, acting as a middleman between providers and insurance companies. They make sure:

- Claim forms are completely and accurately filled out, known as “claim scrubbing”
    - This reduces the chances of denied claims.
- Billing is processed accurately between the insurance company and the provider

For clean electronic claims submitted through clearinghouses, processing can take at least two weeks (https://nybillpro.com/blog/how-long-does-a-medical-bill-take-to-process/)

### Medical Claims Fees

Medical Claims Clearinghouses vary in the fee models in which they charge for claims processing, usually taking around $0.29 to $0.45 per claim or charging a monthly subscription or $70 to $129 (https://www.trillianthealth.com/hubfs/Clearinghouses.pdf)

# VeriSure Product Design

VeriSure aims to cut out the Medical Claims Clearinghouse middlemen and provide a faster, decentralized, and secure way to process medical claims.

## Who will use and benefit from our AVS?

| **User** | **Role in Veri*Sure*** | **Benefit** |
| --- | --- | --- |
| **🏥 Healthcare Providers** | **Submit insurance claims** | **Faster claim approvals & instant payouts** |
| **🏦 Insurance Companies** | **View Submitted, Pending, and Paid claims** | **Reduce fraud, validate claims with ZK proofs** |
| **🏛️ Regulators & Auditors** | **Review flagged claims** | **Verifiable fraud detection without exposing private data** |
| **💻 EigenLayer AVS Validators** | **Process claims on-chain** | **Earn staking rewards for verifying claims** |

# Why Othentic?

- VeriSure benefits from the Performer, Attester, and Aggregator Node architecture of Othentic.
- Performer nodes can be static, randomly chosen, election-based or a staked mechanism
    - In VeriSure, the Performer node will handle the sensitive information, ensuring HIPPA compliance by computing a zero-knowledge proof for the validity of the claim off-chain

# Why zkVM?

- The idea is simple: **low cost and high scalability**
- Generally, zero-knowledge proofs allow us to verify protected health information (PHI) across a community of decentralized nodes without needing to expose PHI to them.
- With zk proofs, we can also enable the verifiability