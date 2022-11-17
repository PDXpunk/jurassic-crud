# Adapted from the excellent starter project at https://github.com/osu-cs340-ecampus/flask-starter-app

from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
from dotenv import load_dotenv, find_dotenv
import os
import database.db_connector as db

# Configuration
app = Flask(__name__)

# Load our environment variables from the .env file in the root of our project.
load_dotenv(find_dotenv())

# database connection info
app.config["MYSQL_HOST"] = os.environ.get("340DBHOST")
app.config["MYSQL_USER"] = os.environ.get("340DBUSER")
app.config["MYSQL_PASSWORD"] = os.environ.get("340DBPW")
app.config["MYSQL_DB"] = os.environ.get("340DB")
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Data used to pre-populate dropdown menus
status_options = ["healthy", "sick", "injured"]
diet_options = ["carnivor", "omnivore", "herbivore"]
electric_status_options = ["online", "reserve", "offline"]
security_status_options = ["online", "lockdown", "offline"]

# Routes 

@app.route('/')
def root():
    return redirect("/dinosaurs")

@app.route('/dinosaurs', methods=["POST", "GET"])
def dinosaurs():
    # Grab Dinosaurs data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all the people in bsg_people
        query = "SELECT Dinosaurs.id AS 'ID', Dinosaurs.name AS 'Name', Species.species_name AS 'Species', Locations.location_name AS 'Location', Dinosaurs.health_status AS 'Status' FROM Dinosaurs INNER JOIN Species ON Dinosaurs.species_id = Species.id INNER JOIN Locations ON Dinosaurs.location_id = Locations.id"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # mySQL query to grab data for dropdowns
        location_query = "SELECT location_name from Locations;"
        cur = mysql.connection.cursor()
        cur.execute(location_query)
        loc_data = cur.fetchall()

        # mySQL query to grab data for dropdowns
        species_query = "SELECT species_name from Species;"
        cur = mysql.connection.cursor()
        cur.execute(species_query)
        spec_data = cur.fetchall()

        # render edit_people page passing our query data and homeworld data to the edit_people template
        return render_template("dinosaurs.j2", data=data, locations=loc_data, 
        spec_data=spec_data)

    if request.method == "POST":
        # fire off if user presses the Add Person button
        if request.form.get("Add_Dinosaur"):
            # grab user form inputs
            species = request.form["species"]
            location = request.form["location"]
            name = request.form["name"]
            status = request.form["status"]

        # TODO: account for null species
            if species == "":
                query = ""
                cur = mysql.connection.cursor()
                cur.execute(query, (species, location, name, status))
                mysql.connection.commit()

        # no null inputs
            else:
                query = "INSERT INTO Dinosaurs(species_id, location_id, name, health_status)\
                    VALUES((SELECT id FROM Species WHERE species_name= %s),\
                    (SELECT id FROM Locations WHERE location_name= %s), %s,\
                    %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (species, location, name, status))
                mysql.connection.commit()

        # redirect back to Dinosaurs page
        return redirect("/dinosaurs")

@app.route('/update_dinosaur/<int:id>', methods=["POST", "GET"])
def update_dinosaur(id):
    # Grab Dinosaurs data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab a specific dinosaur that the user selected
        query = "SELECT Dinosaurs.id AS 'ID',\
            Dinosaurs.name AS 'Name',\
            Species.species_name AS 'Species',\
            Locations.location_name AS 'Location',\
            Dinosaurs.health_status AS 'Status'\
            FROM Dinosaurs\
                INNER JOIN Species ON Dinosaurs.species_id = Species.id\
                INNER JOIN Locations ON Dinosaurs.location_id = Locations.id WHERE Dinosaurs.id = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        data = cur.fetchall()

        # mySQL query to grab data for the location dropdown menu
        location_query = "SELECT location_name from Locations;"
        cur = mysql.connection.cursor()
        cur.execute(location_query)
        loc_data = cur.fetchall()

        # mySQL query to grab data for the species dropdown menu
        species_query = "SELECT species_name from Species;"
        cur = mysql.connection.cursor()
        cur.execute(species_query)
        spec_data = cur.fetchall()

        return render_template("update_dinosaur.j2", 
            data=data, locations=loc_data, 
            spec_data=spec_data, status_options=status_options)

    if request.method == "POST":
        # fire off if user presses the Add Person button
        if request.form.get("Update_Dinosaur"):
            # grab user form inputs
            species = request.form["species"]
            location = request.form["location"]
            name = request.form["name"]
            status = request.form["status"]

        # TODO: account for null species
            if species == "":
                query = ""
                cur = mysql.connection.cursor()
                cur.execute(query, (species, location, name, status))
                mysql.connection.commit()

        # no null inputs
            else:
                query = "UPDATE Dinosaurs\
                    SET species_id = (SELECT id FROM Species WHERE species_name=%s),\
                        location_id = (SELECT id FROM Locations WHERE location_name= %s),\
                        name = %s,\
                        health_status = %s\
                    WHERE id = %s;"
                cur = mysql.connection.cursor()
                cur.execute(query, (species, location, name, status, id))
                mysql.connection.commit()

        # redirect back to Dinosaurs page
        return redirect("/dinosaurs")

# route for delete functionality, deleting a dinosaur from Dinosaurs,
# we want to pass the 'id' value of that dinosaur on button click 
@app.route("/delete_dinosaur/<int:id>", methods=["POST", "GET"])
def delete_dinosaur(id):

    if request.method == "GET":
        # mysql query to gather the form's data
        query = "SELECT Dinosaurs.id AS 'ID', Dinosaurs.name AS 'Name', Species.species_name AS 'Species', Locations.location_name AS 'Location', Dinosaurs.health_status AS 'Status'\
        FROM Dinosaurs\
            INNER JOIN Species ON Dinosaurs.species_id = Species.id\
            INNER JOIN Locations ON Dinosaurs.location_id = Locations.id WHERE Dinosaurs.id = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        data = cur.fetchall()

        return render_template("delete_dinosaur.j2", data=data)


    if request.method == "POST":
        query = "DELETE FROM Dinosaurs WHERE Dinosaurs.id = '%s';"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        mysql.connection.commit()

    # redirect back to dinosaur page
    return redirect("/dinosaurs")

@app.route('/species', methods=["POST", "GET"])
def species():
    # Grab species data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all the Species
        query = "SELECT Species.id AS 'ID', Species.species_name AS 'Species Name', Species.diet AS 'Diet' FROM Species;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        return render_template("/species/species.j2", data=data, diet_options=diet_options)

    if request.method == "POST":
        # fire off if user presses the Add Species button
        if request.form.get("Add_Species"):
            # grab user form inputs
            name = request.form["name"]
            diet = request.form["diet"]

            query = "INSERT INTO Species(species_name, diet)\
                VALUES(%s, %s);"
            cur = mysql.connection.cursor()
            cur.execute(query, (name, diet))
            mysql.connection.commit()

        return redirect("/species")

@app.route('/update_species/<int:id>', methods=["POST", "GET"])
def update_species(id):
    # Grab Species data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab the specific species that the user selected
        query = "SELECT Species.id AS 'ID', Species.species_name AS 'Species', Species.diet AS 'Diet'\
            FROM Species\
            WHERE Species.id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        data = cur.fetchall()

        return render_template("species/update_species.j2", 
            data=data, diet_options=diet_options)

    if request.method == "POST":
        # fire off if user presses the Add Person button
        if request.form.get("Update_Species"):
            # grab user form inputs
            name = request.form["name"]
            diet = request.form["diet"]

            query = "UPDATE Species\
                SET species_name = %s,\
                    diet = %s\
                WHERE Species.id = %s;"
            cur = mysql.connection.cursor()
            cur.execute(query, (name, diet, id))
            mysql.connection.commit()

        # redirect back to Dinosaurs page
        return redirect("/species")

# route for delete functionality, deleting a species from Species,
# we want to pass the 'id' value of that species on button click 
@app.route("/delete_species/<int:id>", methods=["POST", "GET"])
def delete_species(id):

    if request.method == "GET":
        # mysql query to gather the form's data
        query = "SELECT Species.id AS 'ID', Species.species_name AS 'Species Name', Species.diet AS 'Diet' FROM Species\
            WHERE Species.id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        data = cur.fetchall()

        return render_template("/species/delete_species.j2", data=data)


    if request.method == "POST":
        query = "DELETE FROM Species WHERE Species.id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        mysql.connection.commit()

    # redirect back to Species page
    return redirect("/species")


@app.route('/dinosaurAssignments', methods=["POST", "GET"])
def dinosaurAssignments():
    #insert a dino assignment into the table
    if request.method == 'POST':
        #if the user is adding an assignment
        if request.form.get("addDinosaurAssignment"):
            dinosaur = request.form["dinosaur"]
            employee = request.form["employee"]
            description = request.form["description"]
            if employee != "" or dinosaur != "" or description != "":
                emp = employee.split()
                fname = emp[0]
                lname = emp[1]
                query1 = "INSERT INTO Employees_To_Dinosaurs (e_id, d_id, description) \
                        VALUES ((SELECT id FROM Employees WHERE f_name = %s AND l_name = %s), \
                        (SELECT id FROM Dinosaurs WHERE name = %s),  (%s));"
                
                cur = mysql.connection.cursor()
                cur.execute(query1, (fname, lname, dinosaur, description))
                mysql.connection.commit()
        #redirect back to dinosaur assignments
        return redirect('/dinosaurAssignments')

    # get dinosaur assignments data
    if request.method == "GET":
        #SQL to get all the dinosaur assignments
        query2 = "SELECT  Employees_To_Dinosaurs.id AS id, \
            Dinosaurs.name AS 'Dinosaur', CONCAT(Employees.f_name, ' ', Employees.l_name) AS \
            'Employees Assigned', Employees_To_Dinosaurs.description AS 'Assignment' \
            FROM Employees_To_Dinosaurs INNER JOIN Dinosaurs ON Employees_To_Dinosaurs.d_id = \
            Dinosaurs.id INNER JOIN Employees ON Employees_To_Dinosaurs.e_id = Employees.id;"
        cur = mysql.connection.cursor()
        cur.execute(query2)

        dinosaur_assignment_data = cur.fetchall()

        #grab employee data for the drop down
        query3 = "SELECT CONCAT(f_name, ' ', l_name) AS employee FROM Employees"
        cur = mysql.connection.cursor()
        cur.execute(query3)
        employee_data = cur.fetchall()

        # mySQL query to grab certification data for our dropdown
        query4 = "SELECT name FROM Dinosaurs;"
        cur = mysql.connection.cursor()
        cur.execute(query4)
        dinosaur_data = cur.fetchall()

        #render the dinosaurAssignments and pass the nescasary data
        return render_template("dinosaurAssignments.j2", dinosaur_assignments=dinosaur_assignment_data,
         employees=employee_data, dinosaurs=dinosaur_data )


@app.route("/deleteAssignment/<int:id>", methods=["POST","GET"])
def deleteAssignment(id):
    if request.method == "GET":
        query1 = "SELECT  Employees_To_Dinosaurs.id AS id, \
        Dinosaurs.name AS 'Dinosaur', CONCAT(Employees.f_name, ' ', Employees.l_name) AS \
        'Employees Assigned', Employees_To_Dinosaurs.description AS 'Assignment' FROM Employees_To_Dinosaurs \
        INNER JOIN Dinosaurs ON Employees_To_Dinosaurs.d_id = Dinosaurs.id INNER JOIN Employees ON \
        Employees_To_Dinosaurs.e_id =Employees.id WHERE Employees_To_Dinosaurs.id = %s;"

        cur = mysql.connection.cursor()
        cur.execute(query1, (id,))
        data = cur.fetchall()

        return render_template("deleteAssignment.j2", data=data)

    if request.method == "POST":

        query = "DELETE FROM Employees_To_Dinosaurs WHERE Employees_To_Dinosaurs.id = '%s';"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        mysql.connection.commit()

    # redirect back to dinosaur page
    return redirect("/dinosaurAssignments")


@app.route('/employees')
def employees():
    query = "SELECT * FROM Employees;"
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    return render_template("employees.j2", data=data)


@app.route('/locations', methods=["POST", "GET"])
def locations():

    if request.method == "GET":

        # mySQL query to grab data for the species dropdown menu
        species_query = "SELECT species_name from Species;"
        cur = mysql.connection.cursor()
        cur.execute(species_query)
        species_list = cur.fetchall()

        # mySQL query to grab permitted species data
        permitted_species_query = "SELECT Locations.id, Species.species_name\
            FROM Locations\
            INNER JOIN Species_Allowed_Locations ON Locations.id = Species_Allowed_Locations.l_id\
            INNER JOIN Species ON Species_Allowed_Locations.s_id = Species.id;"
        cur = mysql.connection.cursor()
        cur.execute(permitted_species_query)
        permitted_species = cur.fetchall()

        query = "SELECT Locations.id AS 'ID',\
            Locations.location_name AS 'Name',\
            Locations.electric_grid_status AS 'Electricity',\
            Locations.security_status AS 'Security'\
            FROM Locations;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("/locations/locations.j2", data=data, species_list=species_list, permitted_species=permitted_species,
            security_status_options=security_status_options, 
            electric_status_options=electric_status_options)

    if request.method == "POST":
        # fire off if user presses the Add Species button
        if request.form.get("Add_Location"):
            # grab user form inputs
            name = request.form["name"]
            electrical = request.form["electrical"]
            security = request.form["security"]
            print(name, electrical, security)

        query = "INSERT INTO Locations(location_name, electric_grid_status, security_status)\
            VALUES(%s, %s, %s);"
        print(query)
        cur = mysql.connection.cursor()
        cur.execute(query, (name, electrical, security))
        mysql.connection.commit()

        return redirect("/locations")

@app.route("/delete_location/<int:id>", methods=["POST", "GET"])
def delete_location(id):

    if request.method == "GET":
        # mySQL query to grab permitted species data
        permitted_species_query = "SELECT Locations.id, Species.species_name\
            FROM Locations\
            INNER JOIN Species_Allowed_Locations ON Locations.id = Species_Allowed_Locations.l_id\
            INNER JOIN Species ON Species_Allowed_Locations.s_id = Species.id;"
        cur = mysql.connection.cursor()
        cur.execute(permitted_species_query)
        permitted_species = cur.fetchall()

        query = "SELECT Locations.id AS 'ID',\
            Locations.location_name AS 'Name',\
            Locations.electric_grid_status AS 'Electricity',\
            Locations.security_status AS 'Security'\
            FROM Locations\
            WHERE Locations.id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        data = cur.fetchall()

        return render_template("/locations/delete_location.j2", data=data, permitted_species=permitted_species)


    if request.method == "POST":
        query = "DELETE FROM Locations WHERE Locations.id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        mysql.connection.commit()

    # redirect back to Species page
    return redirect("/locations")


@app.route('/update_location/<int:id>', methods=["POST", "GET"])
def update_location(id):
    # Grab Species data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab permitted species data
        permitted_species_query = "SELECT Locations.id, Species.species_name\
            FROM Locations\
            INNER JOIN Species_Allowed_Locations ON Locations.id = Species_Allowed_Locations.l_id\
            INNER JOIN Species ON Species_Allowed_Locations.s_id = Species.id;"
        cur = mysql.connection.cursor()
        cur.execute(permitted_species_query)
        permitted_species = cur.fetchall()

        query = "SELECT Locations.id AS 'ID',\
            Locations.location_name AS 'Name',\
            Locations.electric_grid_status AS 'Electricity',\
            Locations.security_status AS 'Security'\
            FROM Locations\
            WHERE Locations.id = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (id,))
        data = cur.fetchall()

        return render_template("locations/update_location.j2", 
            data=data, permitted_species=permitted_species, security_status_options=security_status_options, 
            electric_status_options=electric_status_options)

    if request.method == "POST":
        # fire off if user presses the edit location button
        if request.form.get("Update_Location"):
            # grab user form inputs
            name = request.form["name"]
            electrical = request.form["electrical"]
            security = request.form["security"]

            query = "UPDATE Locations\
                SET location_name = %s,\
                    electric_grid_status = %s,\
                    security_status = %s\
                WHERE Locations.id = %s;"
            print(query)
            cur = mysql.connection.cursor()
            cur.execute(query, (name, electrical, security, id))
            mysql.connection.commit()

        # redirect back to Dinosaurs page
        return redirect("/locations")

@app.route('/visitors')
def visitors():
    query = "SELECT * FROM Visitors;"
    cur = mysql.connection.cursor()
    cur.execute(query)
    results = cur.fetchall()
    return render_template("visitors.j2", Visitors=results)
# Listener

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 1857)) 
    
    app.run(port=port, debug=True) 