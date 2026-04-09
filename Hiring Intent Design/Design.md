# Hiring Intent Design Logic

The goal in this design is predict how eager a company to really making a hiring in near term ? 
Instead of purely relying on the job advertisement, I would combine different kind of signals the measure how serious this company to make a hiring. Because some companies grow actively, some just keep on the advertisements and some just make selection for few critical roles. 

### Signals to use
I would combine multiple signal groups together to understand hiring intent, because I think if multiple sources producing the same point, then I can accept that as a signal for a decision making. 

1. Job Posting Signals
One of the direct signals to investigate is the action of job advertisements. With this in mind I look at the how many new posts were opened in 30/60/90 days. How many of them are actively open. How many different departments the posts spread accross. How much locations are there that is actively hiring. Whether the same role is being opened frequently. How long the posts remain open. Because instead of just saying "There are posts", the volume, distribution and the frequency is meaningful. For example; just an old post is a weak signal. But hirings on different departmants at the same should be considered as a strong signal. 

2. Company Growth 
While job postings should be considered as meaningful signal, the growth motion should also be meaningful in terms of hiring intent. Therefore in this aspect I search for the followings: employee growth, investment and funding news, entering to a new market, opening a new office, leadership hiring, operation expansions. While these signals can be considered as positive growth, we also have to keep in mind the negative growth. This can be understandable from layoffs, hiring freeze, signs of downsizing and so on. 

3. Recruiter Activities
If a company is active in terms of hiring, then this should be also visible from the human activities on the hiring side. This can be captured from: number of recruiters, recruiter activites, "hiring" like messages on LinkedIn like websites. 

4. Historical Behaviours
Also a company's past behviour is also important. Whether there was actual growth when they posted job openings in the past, are there any seasonal hiring behaviour, whether past hiring spikes yielded real results. Based on these past movements, we can understand whether the company is actually making a hiring or just constantly posting job openings. 

At the first version, instead of relying on ML models, I create a wieghted rules based scoring method. This way, since we are at the begining stage, we can have trust on system. The other important thing is that we explain the behaviour of the system to optimize. We can create a fast prototype, can easily see false positives and easy to debug/maintain. So the color of the first step should be: establisihng reasonable, explainable and reliable system.

### Scoring Logic
After defining the signal logics, we should not purely put them into single equation. Instead we should define weights to our signals, to have a single score. So this way we have this logic: Hiring intent of a company would not be understand from the number of postings instead, how contextually connected these postings are. 

### Feature Processing
This step is cruical to obtain meaningful values from our signals. Instead of purely using these signals, we need to re-frame their values into same window. For example; a company with 50 employees that posts 20 job openings should not be considered same signal with another comopany with 10k employees that posts 20 job postings. Instead we should normalize the number of postings with the number of employee count and so on. 


### Confidence Score
When we obtain a final score, we can not just purely rely on it. Even tough the system yields high score, we should check the sampling size. Therefore we need to measure how safe to rely on our final score. This brings us to calculation of confidence score. 

#### Coverage
How many different signals do I have ? In this logic we say the following: If multiple signals are pointing to same point, it is more reliable than a single signal that also points same. 

#### Consistency
Even tough we have multiple signals that are active, they also should be point into same way. Too many job postings, employee growth, recruiter activity -> Signals are consistent
Many job postings, layoff signals at the same time, high stale post rate -> Signals are incosistent therefore we can not rely on them.

#### Freshness
Time can not be ignored. Fresh signals are more powerfull than old ones. 

### Output
So as we calculated our scores, we can not yield a single value. If we can then what is point of not using ML models? Therefore since reliability and eplainability is important in terms of business, we need a combination of elements in our output. Elements like, hiring intent score, confidence score, score breakdown, strongest positive/negative signals and human explanation. Example output should be the following: 
- Hiring intent: High
- Confidence: Medium-High
- Main reason: last 30-days job post growth, multi departmant hiring, recent expansion signal
- Risk note: some reposted jobs detected

This is very important for this system to work, because it contains **explainability** which brings cause-effect relation for further improvements. 

### Explainability
We should be able to explain why the system behaves like that in any situation. 

1. Top Signals
We should be able to directly display the top signals

2. Group level debugging
Since we have different kind of signals, which they represent different kind of groups, we should be able to compare and tell which groups/signals are strong or weak

3. Human Explanation
For easy understanding, by combining the top signals and group level debugging we should be able to express the actions of the system. 

### Result of Further Iterations
Since we required reliability, easy debugging, fast prototyping and explainability we begin with rule-based system. As the system works, we can gather historical **labeled** data. The labels can be derived from: 
- Was hiring actually made
- Was there an outreach return
- Did the headcount increased
- Were the open roles filled

Even tough the ML model can behave more dynamic in different variants of patterns, we should not give up on the explainability. Therefore we can create a hybrid-approach. We can use rule-based scoring for business logic, ML score for probability, and yield a final output by combining both. 


### Risk and Limitations
1. Ghost postings
Some companies post job openings but don't actually hire quickly.

2. Stale data
Outsourcing may be delayed or incomplete.

3. Company size bias
If not normalized, large companies will consistently score high.

4. Sector effects
Hiring may be seasonal in some sectors; this can be misinterpreted.

5. Mixed signals
A company experiencing layoffs may still be hiring for some critical roles.

6. Missing data
Recruiter and growth signals may not be visible in small or private companies.

### Final Approach
Using the MVP output, we can have multi-signal approach, weighted rule based scoring, seperate confidence scores, explainable outputs. At the further iterations we can add ML mode with historical labels, feedback loop, sector-specific tunning.