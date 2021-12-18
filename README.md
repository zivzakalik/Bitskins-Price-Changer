# Bitskins Price Changer
The program runs in the background, and updates the item's price to be the lowest of all the items of the same type, within the chosen lower and upper bounds.

## Usage

The program updates the prices every 60 seconds as long as it runs. It does not update the site while you are in the price updating menu. If you dont want to change anything you can type "skip" to just keep updating the prices on the site.

You can change accounts by typing "logout" when looking at the price updating menu.

You can also run 2 different accounts at the same time. Create 2 folders with 2 seperate myItemsdb.json files and run the program from the same folder.

## Use case:

If I put a knife on sell and set the minimal price on 30 and maximal on 40, there are 3 options.

First one is that the cheapest one available is 36.66$. The program will set my knife to be 36.65$, since it is within bounds, and I want my item to be the cheapest within that range so that it shows up first on the list.

Second is that the lowest one available is 45.55$. The program will set the price on 40$, since its the upper bound I chose, and with that price, the item will show up first on the list.

Third one is the the cheapest is 10$. The program will set the price at 30$, at my lower limit, since I want the item to show up first on the list, but only if the lowest price is within the chosen range - any lower than that is too low for me.
