Multiple-Choice Questions on Software Engineering Failure Modes

- 9/15 version 1.0

---

1 What is the correct distinction between a fault, an error, and a failure?
1. A fault is user-visible, an error is internal, and a failure is a flaw in the code
2. _**A fault is a flaw in the system, an error is that fault becoming active internally, and a failure is when the system stops delivering its service to users**_ 
3. A fault and an error are the same thing; a failure is simply a more severe fault
4. A failure always causes an error, which always causes a fault, in that order
5. Do not know

---

2 A gray failure is best described as a situation where:
1. The whole system is down for every user at the same time
2. A fault exists but has not yet been triggered by any condition
3. _**The system believes it is healthy and passes its own health checks while real users experience it as broken**_
4. A single component fails and shifts its load onto the remaining components
5. Do not know

---

3 What is the defining characteristic of a metastable failure?
1. It only affects a single region or a single subset of users
2. _**It sustains itself through a feedback loop even after the original trigger has completely gone away, so removing the cause does not fix it**_
3. It is resolved automatically once the system is left alone for a few minutes
4. It is always caused by an expiring TLS certificate
5. Do not know

---

4 What distinguishes a hard dependency from a soft dependency?
1. A hard dependency is external, while a soft dependency is always internal
2. A hard dependency is synchronous, while a soft dependency is always asynchronous
3. _**A hard dependency is one the operation cannot complete without, while a soft dependency is one the operation can survive without, often by running in a degraded form**_
4. A hard dependency is one your team owns, while a soft dependency belongs to a third party
5. Do not know

---

5 As a resource approaches saturation, what is typically the first observable symptom?
1. Outright errors and rejected requests
2. _**Rising latency, as work begins to wait for the resource before anything actually errors out**_
3. A complete and immediate loss of the internal heartbeat
4. There are usually no observable symptoms.
5. Do not know

---

6 Why are latent faults considered particularly dangerous?
1. They are usually caused by a recent code deploy
2. They immediately degrade performance the moment they are introduced
3. They can only be detected after a total system outage has occurred
4. _**They sit dormant and invisible during normal operation, so the system looks healthy right up until a trigger activates them**_
5. Do not know

---

7 A team runs three replicas of a service and assumes this makes an outage nearly impossible. Which situation shows that this redundancy can be an illusion?
1. The three replicas each handle a different type of request
2. _**All three replicas share a common cause, such as the same rack, the same bad deployment, or the same upstream database, so one event takes all three down together**_
3. The three replicas are not located in three separate availability zones
4. Each replica has its own independent power supply and network path
5. Do not know

---

8 Why do good operators deliberately leave headroom rather than running a system near full capacity?
1. Because idle capacity reduces the power costs of the servers
2. Because latency falls linearly as utilization rises, so headroom is cheap insurance
3. **_Because latency does not rise linearly; near full utilization, waiting time curves upward sharply, so the last sliver of capacity is extraordinarily expensive_**
4. None of the above
5. Do not know

---

9  Risk tolerance differs from risk appetite in that tolerance:
1. Is a forward-looking, aspirational statement set at the enterprise level
2. Defines the maximum loss the organization can survive before collapse
3. _**Translates appetite into operational thresholds of acceptable deviation, often expressed as KPIs or SLA limits**_
4. Applies only to hardware failures rather than business outcomes
5. Do not know

---

10 Which relationship describes a sustainable risk posture?
1. Actual risk > risk appetite > risk capacity
2. _**Risk capacity > risk appetite > actual risk**_
3. Risk appetite > risk capacity > actual risk
4. Risk tolerance > risk capacity > risk appetite
5. Do not know

--- 

## End