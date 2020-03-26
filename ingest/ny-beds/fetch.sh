#!/bin/bash

wget https://health.data.ny.gov/api/views/vn5v-hh5r/rows.json?accessType=DOWNLOAD -O nys-facilities.json
wget https://health.data.ny.gov/api/views/2g9y-7kqm/rows.json?accessType=DOWNLOAD -O nys-beds.json

