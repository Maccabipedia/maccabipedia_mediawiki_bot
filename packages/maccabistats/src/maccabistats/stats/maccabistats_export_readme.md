# MaccabiPedia data

The nearby files contains the data we have in MaccabiPedia (https://maccabipedia.co.il).  
Some of the fields may be empty (such as stadiums or goal-type) or contain partial data (such as assist) -  
take this into consideration while analyzing the data, we are still trying to fill every data we can.

# Intro

Each game in MaccabiPedia is built from many "player events", each one is an occurrence from the game,  
such as: Player started the game as part of the line-up, got a yellow card, was the captain and so on.

In addition we save data at the game level, both of these data types are described below, where player_event described on section 1 and game_data on section 2.


1. Player Data
    * player_name
    * player_number
    * player_time_occur: The minute this event occurred at
    * player_event_type
       1. ScoreGoal
       2. RedCard
       3. YellowCard: Yellow card which is not part of future red card (2 yellows)
       4. FirstYellowCard: First yellow card out of two
       5. SecondYellowCard: Second yellow card out of two (should be counted as red card)
       6. LineUp
       7. SubstitutionIn
       8. SubstitutionOut
       9. AssistGoal
       10. Captain
       11. PenaltyMissed
       12. PenaltyStopped: Goalkeeper event only
       13. Benched
       14. Unknown
    * player_goal_type:
       1. FreeKickGoal
       1. PenaltyGoal
       1. HeaderGoal
       1. OwnGoal
       1. BicycleKickGoal
       1. NormalGoal: The goal is not relevant for every other category
       1. UnknownGoal
    * player_assist_type:
        1. NormalAssist: The assist is not relevant for every other category
        1. FreeKickAssist
        1. CornerAssist
        1. ThrowInAssist
        1. PenaltyWinningAssist
        1. UnknownAssist
    * player_team: The name of the team this player belongs to
2. Game Data
    * stadium
    * date: lowest resolution will be mostly - hour
    * crowd
    * referee
    * competition: We write the specific competition name, for example: "Ligat ha'al" and "Liga leumit" will count as different competitions, you can merge them in your analytics if such required
    * fixture: Which round in the competition is played?
    * season
    * technical_result: Whether this game ends by forfeit of one of the team, or in any non-regular decision, In this case the displayed scores may not reflect the final decided result, but the in-game score
    * home_team_name
    * home_team_score
    * home_team_coach
    * away_team_name
    * away_team_score
    * away_team_coach
    
    
# Exported files
When exporting the data out of MaccabiStats you may find two files:
* 'player_events' - each record in this file is combination of: a player occurrence (section 1 above) and the current game data (section 2), which means that for every game we will export many records.
* 'games_data' - each record in this file is a dump of the game information we have on MaccabiStats (section 2 above), each game will have one record only.    
    
    
# Code
Make sure to check out our Github repositories at:
* [MaccabiStats Repository](https://github.com/Maccabipedia/maccabistats)
* [MaccabiPedia Organization](https://github.com/Maccabipedia)
    
# Contact Us
We will be glad to help with any question or hear your new ideas and requests,  
you can contact us at:
* [MaccabiPedia Telegram](https://t.me/MaccabiPedia)
* maccabipedia@gmail.com
* [MaccabiPedia website](https://www.maccabipedia.co.il/עמוד_ראשי)
