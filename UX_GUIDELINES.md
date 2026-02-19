# ReedManage UX Guidelines: Interpretation Anxiety & Diagnostic Design

**Created**: January 27, 2026
**Purpose**: Ethics-to-UX translation layer for engineers and designers
**Core Principle**: Diagnosis, not competition

---

## Why This Document Exists

When you show users "top 28%" or "community average," some will feel motivated, others will feel judged.

**This document prevents accidental Dark Patterns** by defining how comparisons must be framed to respect craft diversity and normalize variance.

Engineers and designers can move fast without re-debating philosophy every time.

---

## Core UX Principle

### **Comparisons as Diagnosis, Not Ranking**

**The Problem**: Percentiles and rankings trigger interpretation anxiety
- Some users feel motivated ✅
- Others feel inadequate ❌
- Same data, opposite emotional responses

**The Solution**: Contextual framing that normalizes variance

Users need to understand:
1. Variation is **normal** in reed making
2. Different styles produce different results
3. Data reflects **reported outcomes**, not absolute quality
4. Many factors beyond metrics affect performance

---

## Copy Patterns: DO vs. DON'T

### ❌ **DON'T: Competitive Framing**

```
You're ranked #127 out of 500 oboists!

Your reeds are worse than 74% of the community.

You need to improve to catch up with top performers.

LEADERBOARD:
1. User_8472 (4.9⭐)
2. User_3291 (4.8⭐)
3. User_7621 (4.7⭐)
...
127. YOU (3.2⭐)
```

**Why This Fails:**
- Creates shame and comparison anxiety
- Implies universal standards in a craft with diverse styles
- Ignores context (instrument, experience level, goals)
- Gamifies craft, turning art into competition

---

### ✅ **DO: Diagnostic Framing**

```
Your Average Reed Quality: 3.8 ⭐
Community Average: 3.4 ⭐

You're in the top 28% of oboists—but remember:
• Variation is normal in reed making
• Different styles produce different results
• This reflects reported outcomes, not absolute quality
• Many factors beyond these metrics affect performance

Your Most Successful Cane Brand: Rigotti (avg 4.1⭐)
Community Favorite: Glotin (42% of top-rated reeds)
Popular choice in your region: Bonazza

💡 What this means:
Your approach is working well for you. If you're looking to
experiment, consider trying Glotin—it's widely successful
among oboists with similar parameters to yours.
```

**Why This Works:**
- Acknowledges user success first
- Provides context that normalizes variance
- Offers actionable insights without judgment
- Frames suggestions as experiments, not requirements
- Respects craft diversity

---

## Required Copy Elements for All Comparisons

Every comparison feature MUST include:

### 1. **The Data** (clear, honest numbers)
- Your metric vs. community metric
- Percentile if relevant
- Sample size for context

### 2. **The Context** (normalization language)
Choose at least 2:
- "Variation is normal in reed making"
- "Different styles produce different results"
- "This reflects reported outcomes, not absolute quality"
- "Many factors beyond these metrics affect performance"
- "Your goals may differ from community averages"

### 3. **The Interpretation** (what it means)
- Start with affirmation or neutral framing
- Explain significance in craft terms
- Suggest experiments, not requirements
- Use "consider" not "should"

### 4. **The Invitation** (optional next step)
- Phrase as experiment: "Consider trying..."
- Not directive: "You should..."
- Respect user autonomy
- Make it easy to ignore

---

## Voice & Tone Rules

### **Affirmative Before Corrective**

❌ "Your success rate is below average. You need to improve."
✅ "You've logged 47 reeds—great data! Your success rate is 58% (community: 65%). This suggests an opportunity to experiment with different parameters."

### **Curious, Not Prescriptive**

❌ "You should switch to medium hardness cane."
✅ "Oboists using medium hardness report 12% higher success rates. Worth exploring?"

### **Normalize Variance Everywhere**

❌ "Most users get better results than you."
✅ "Reed making is highly individual—your 3.2⭐ average reflects your style and goals, which may differ from the 3.4 community average."

### **Respect Expertise**

❌ "Beginners should start with..."
✅ "Many oboists starting out find medium hardness easier to work with, though experienced makers often prefer harder cane for specific tonal qualities."

---

## Specific Feature Guidelines

### **"How Am I Doing?" Dashboard**

**Purpose**: Help users understand their craft trajectory
**NOT**: Rank users against each other

**Required Elements:**
1. User's key metrics (quality, success rate, consistency)
2. Community averages with sample sizes
3. Contextual disclaimers (variation is normal)
4. Actionable insights framed as experiments
5. Regional/instrument-specific comparisons when relevant

**Example Structure:**
```
[YOUR METRICS]
Clear, prominent display of user data

[COMMUNITY CONTEXT]
How your metrics relate to similar users
+ Normalization language (at least 2 phrases)

[INSIGHTS]
What patterns emerge from your data
Suggested experiments based on successful approaches

[AFFIRMATION]
Recognize progress, effort, or unique strengths
```

---

### **Percentiles: How to Display**

**The Challenge**: "Top 28%" sounds competitive
**The Fix**: Add immediate context

❌ **Bad:**
```
You're in the top 28% of oboists! 🏆
```

✅ **Good:**
```
You're in the top 28% of oboists—but remember:
• This reflects reported data, not absolute quality
• Reed making is highly individual
• Different approaches work for different players

Your approach is working well for you.
```

**Visual Treatment:**
- Don't use trophy emojis, gold stars, or podium imagery
- Use subtle colors (soft blues/greens, not golds/reds)
- Avoid progress bars that feel like "leveling up"
- Consider showing distribution curves instead of single percentiles

---

### **Brand Recommendations**

**Purpose**: Help users discover what works for others
**NOT**: Pressure users to conform

❌ **Bad:**
```
Top performers use Glotin. You should too!
Switch now for better results.
```

✅ **Good:**
```
Your Most Successful Brand: Rigotti (4.2⭐ average)

Among oboists with similar preferences:
• Glotin is popular (used by 38%)
• Rigotti has high satisfaction (4.1⭐ average)
• Bonazza shows consistent results (3.9⭐ average)

💡 Your Rigotti results are already strong. If you're curious
about alternatives, Glotin might be worth exploring.
```

---

### **Success Rate Comparisons**

**The Sensitivity**: Success rate feels personal
**The Approach**: Frame as diagnostic, not evaluative

❌ **Bad:**
```
Your success rate: 52%
Community average: 68%
You're failing more reeds than most users.
```

✅ **Good:**
```
Your Success Rate: 52% (31 successful reeds out of 60)
Community Average: 68% (based on 1,247 oboists)

This difference might reflect:
• Your standards for "successful" (stricter grading?)
• Experimentation phase (trying new techniques?)
• Different goals (exploring tone variety vs. consistency?)
• Natural variation in the craft

Lower success rates often indicate active learning and
experimentation—both valuable for craft development.

💡 If you'd like to explore patterns, check which parameters
correlate with your successful reeds.
```

---

## Anti-Patterns to Avoid

### **1. Gamification That Becomes Toxic**

❌ Leaderboards with usernames
❌ "Beat your friends!" framing
❌ Streaks that create pressure ("Don't break your 47-day logging streak!")
❌ Achievements that feel mandatory ("Unlock Pro Reed Maker status!")

✅ Personal milestones ("You've logged 100 reeds!")
✅ Opt-in challenges ("30-day reed logging challenge—join if interested")
✅ Collaborative goals ("Community unlocked: 10,000 reeds analyzed!")

### **2. Implied Judgment**

❌ "Your reeds need improvement"
❌ "Low quality detected"
❌ "You're falling behind"
❌ "Catch up with the community"

✅ "Your average quality is 2.8⭐"
✅ "Opportunity to experiment with different parameters"
✅ "Your trajectory shows learning and growth"
✅ "Your approach differs from common patterns—explore why"

### **3. Decontextualized Metrics**

❌ Showing percentiles without explanation
❌ Comparing beginners to experts
❌ Ignoring instrument differences (oboe vs. bassoon)
❌ Universal standards for diverse goals

✅ Always provide context
✅ Segment by experience level when possible
✅ Instrument-specific comparisons
✅ Acknowledge goal diversity

---

## Copy Templates for Common Scenarios

### **User Above Average**

```
Your average quality: [X]⭐
Community average: [Y]⭐

Your results are strong. [Specific insight about their patterns]

💡 [Optional experiment suggestion]
```

### **User Below Average**

```
Your average quality: [X]⭐
Community average: [Y]⭐

Remember: Reed making is highly individual, and this data
reflects reported outcomes across diverse styles and goals.

Your [positive pattern from their data, e.g., "consistency
has improved 23% over the last month"].

💡 [Specific actionable insight]: Oboists with similar
parameters who use [X] report [Y]% higher success. Worth exploring?
```

### **User New to Platform (< 10 reeds)**

```
You've logged [N] reeds—great start!

Community comparisons become more meaningful after 20+
reeds, when patterns emerge. For now, focus on tracking
what you notice about each reed.

💡 Consider noting: What made this reed successful (or not)?
These observations become valuable as your dataset grows.
```

### **User with Unusual Patterns**

```
Your data shows interesting patterns that differ from
common approaches:

• [Specific unique pattern]
• [How it differs from community]

This isn't good or bad—it reflects your personal style.
Reed making is a craft with many valid approaches.

💡 Your unique approach might reveal insights others
would find valuable. Consider sharing your methodology
in the community forum (optional).
```

---

## Visual Design Principles

### **Colors**

❌ Red/green for bad/good (too judgmental)
❌ Gold/silver/bronze (competitive)
❌ Bright, urgent colors (anxiety-inducing)

✅ Soft blues and greens (calm, informative)
✅ Neutrals for most data (gray, light colors)
✅ Subtle highlights for insights (muted indigo)

### **Icons**

❌ Trophies, medals, ribbons
❌ Checkmarks/X marks for quality (implies right/wrong)
❌ Arrows pointing up/down with value judgment

✅ Info icons for contextual help
✅ Light bulbs for insights and suggestions
✅ Subtle trend indicators (neutral presentation)
✅ Regional/community icons without hierarchy

### **Typography**

❌ Large, bold percentiles without context
❌ ALL CAPS for rankings
❌ Tiny disclaimers that hide context

✅ Equal visual weight for data and context
✅ Larger text for interpretations than raw numbers
✅ Disclaimers integrated naturally, not hidden

---

## Testing for Interpretation Anxiety

### **Before Shipping Any Comparison Feature**

Run these tests:

1. **The Below-Average Test**
   - Simulate a user performing worse than community average
   - Does the copy feel judgmental or diagnostic?
   - Would you feel worse about your craft after reading it?

2. **The Beginner Test**
   - Show the feature to someone new to reed making
   - Do they understand what the numbers mean?
   - Do they feel welcomed or intimidated?

3. **The Expert Test**
   - Show to an experienced reed maker
   - Does it respect their expertise?
   - Would they find it useful or patronizing?

4. **The Diversity Test**
   - Consider users with different goals:
     - Professional oboist seeking consistency
     - Student experimenting and learning
     - Bassoonist (different standards than oboe)
     - Historical instrument player (very different approach)
   - Does the feature serve all these users fairly?

---

## When to Show Comparisons

### **Good Times:**
- User has 20+ reeds logged (meaningful patterns)
- User opts in to Premium/Contributor tier
- User explicitly requests insights
- Data shows clear, actionable patterns

### **Bad Times:**
- User just signed up (no context yet)
- User is in experimental/learning phase
- Sample sizes too small (< 10 community members in comparison group)
- Data shows no clear patterns (might create false insights)

---

## Handling Edge Cases

### **Outlier Users (Far Above or Below Average)**

**Don't:**
- Make them feel like a failure or superhuman
- Suggest they're doing everything wrong
- Ignore their unique circumstances

**Do:**
```
Your average quality: [X]⭐
Community average: [Y]⭐

Your results are notably [higher/lower] than typical patterns.
This often indicates:
• [Specific explanations relevant to their data]
• Unique goals or playing style
• Different quality standards

Reed making is deeply personal. If your current approach
meets your musical needs, that's what matters most.

💡 If you're interested in exploring community patterns,
[specific actionable insight]. But there's no "correct" way
to make reeds—only what works for you.
```

### **Users Who Game the System**

**Issue**: Some users might inflate quality ratings to "win"

**Solution**:
- Don't create incentives to game metrics
- No rewards for high ratings
- Frame quality as personal reference, not competition
- If gaming detected, gentle reminder:

```
We noticed your recent reeds are all rated 5⭐. That's great
if they're genuinely exceptional!

Remember: Quality ratings are most useful when they're honest.
Lower ratings help identify patterns and improve your craft.
Community comparisons are based on diverse, realistic ratings.
```

### **Users Who Feel Pressured to Contribute Data**

**Issue**: Some users might feel guilty for staying on Free tier

**Solution**:
- Prominently display: "FREE tier is fully featured and private—no obligations"
- Never show comparison of Free vs. Contributor users
- No countdown timers or pressure tactics
- Gentle reminder at most:

```
💡 Enjoying ReedManage? Contributors get Premium features
FREE by sharing anonymized data. Learn more (no pressure!)
```

---

## Language Guide: Word Choices Matter

### **Preferred Terms:**

| Use This | Not This |
|----------|----------|
| "Community average" | "Normal" or "Standard" |
| "Your approach" | "Your method" (sounds cold) |
| "Consider trying" | "You should" / "You must" |
| "Opportunity to explore" | "Problem" / "Issue" |
| "Patterns suggest" | "You're doing X wrong" |
| "Experiment with" | "Fix" / "Correct" |
| "Your results show" | "You failed" / "You succeeded" |
| "Among similar players" | "Better players" |
| "Variation is normal" | "Everyone else" |
| "Reported outcomes" | "Success" / "Failure" |

---

## Accessibility Considerations

### **For All Comparison Features:**

1. **Screen Reader Friendly**
   - Alt text for charts/graphs
   - Logical heading structure
   - Clear data table formats

2. **Color Blindness**
   - Never rely solely on color to convey meaning
   - Use text labels, icons, and patterns

3. **Cognitive Load**
   - Don't overwhelm with too many metrics at once
   - Progressive disclosure: summary → details
   - Clear visual hierarchy

4. **Anxiety-Friendly Design**
   - Gentle language throughout
   - Easy to dismiss/hide comparisons if overwhelming
   - No persistent notifications about rankings

---

## Implementation Checklist

Before shipping any comparison feature:

- [ ] Data presented clearly and accurately
- [ ] Context provided (at least 2 normalization phrases)
- [ ] Interpretation explains significance without judgment
- [ ] Suggestions framed as experiments, not requirements
- [ ] Below-average users don't feel inadequate
- [ ] Above-average users don't feel superior
- [ ] Visual design is calm, not competitive
- [ ] Copy reviewed against this guide
- [ ] Tested with diverse user scenarios
- [ ] Accessibility requirements met
- [ ] Easy to understand at a glance
- [ ] Option to hide/dismiss if desired

---

## Final Principle

**When in doubt, ask:**

> "If I were a user seeing this comparison for the first time,
> and my metrics were below average, would I feel:
>
> A) Curious and empowered to experiment?
> B) Judged and inadequate?"

If the answer is B, rewrite with more context and gentler framing.

---

## Updates and Evolution

This guide will evolve as we learn from user feedback.

**Document Owner**: Product Design Lead
**Review Cycle**: Quarterly
**User Feedback Loop**: Monitor support tickets and community discussions for signs of interpretation anxiety

**When users say:**
- "I feel like I'm bad at this" → Review framing
- "Why am I being compared to others?" → Add more context
- "This makes me anxious" → Soften language
- "I don't understand what this means" → Clarify interpretation

---

## Summary: The Three Laws of Diagnostic Design

1. **Diagnosis, not competition**: Every comparison must help users understand their craft, not judge their worth

2. **Context is mandatory**: Raw metrics without normalization language create anxiety

3. **Respect autonomy**: Suggestions are experiments, never requirements

**Remember**: You're not building a game. You're building infrastructure for a craft. Treat it with the respect it deserves.

---

**If engineers and designers follow this guide, accidental Dark Patterns become impossible.**

The philosophy is locked into the UX.
