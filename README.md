# Inventory-Control-Web_V1

Inventory Control WebV1 is a web based inventory reporting dashboard. This application displays plots based on data from a MySQL database. 
I used the Streamlit Framework with Python to create an interactive and accurate data reporting application.

![pic1](https://github.com/user-attachments/assets/7b0d634a-c079-4695-b433-302805871724)

### Main Inventory Dashboard
Here the user can see the overall inventory, item count and item details. The user can select what year and month the data will be from.
![pic2](https://github.com/user-attachments/assets/dd42baa7-8bf5-4b4a-aabf-d8880f498b77)


The first bar graph displays the count for the year and month selected. If you hover over each bar in the plot you can see more details about the item. The user can select what items were counted as spools as well.
![pic3](https://github.com/user-attachments/assets/3608ac5a-7699-4b96-8d0c-1d19f913dc14)


This is a bar graph displaying overall distrubution and metrics of items in inventory by item type. If you hover over each bar you can see what items are in each category and count details.
![pic4](https://github.com/user-attachments/assets/609dc02f-39be-45c2-8e36-7de8069739a7)

You can compare item inventory for one or multiple items from different years or the same.(Will add fix to sort years from earliest -> latest -> current)
![pic5](https://github.com/user-attachments/assets/46b0e0af-b026-43c7-b569-3d645468e952)
![pic6](https://github.com/user-attachments/assets/b7573659-2b07-48cd-ab8a-f831f02e55e2)

# Tab for more user options.
![pic7](https://github.com/user-attachments/assets/315cf255-a165-466b-8c66-a12ebfdc1c31)

### Add or Remove Item Page
This page is used to adjust inventory counts of an item. If a employee removes an item for inventory, that employee will select the BTN_SKU, once selected, the inventory data of that item will appear. The employee has to enter how many boxes to add or remove, and the total units in the box of that item. The 'Current Average Units Per Box/Roll' changes everytime an item is added or removed, this is to help get a more accurate count.  
![pic8](https://github.com/user-attachments/assets/ec4e7ea1-5221-4c18-8fd7-823c97e04311)
![pic9](https://github.com/user-attachments/assets/1bdcf0c4-ce1c-469c-be78-6b40faf046fc)

You can view the adjustment history for an item in the next section of the page.
![pic10](https://github.com/user-attachments/assets/b07bb9bb-2a13-440e-91ef-56149b0fdab9)



