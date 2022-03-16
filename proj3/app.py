from datetime import date
import json
import os
from pathlib import Path
from datetime import datetime

import apps
import hydralit as hy
import hydralit_components as hc
import streamlit as st
from dotenv import load_dotenv
from hydralit import HydraApp
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

load_dotenv()

############################################################################################################################################################################
# Load Contract
############################################################################################################################################################################

def load_contract():

    #Load ABI
    with open(Path('./contracts/compiled/medrecord.json')) as f:
        contract_abi = json.load(f)
    
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    contract = w3.eth.contract(
        address = contract_address,
        abi = contract_abi
    )

    return contract

contract = load_contract()

############################################################################################################################################################################
# Helper functions to pin files and json to Pinata
############################################################################################################################################################################

def pin_chart(hospital_input, docname_input, pat_address, record_date, age_input, height_input, weight_input, med_his_notes, exam_notes):

    # Build a token metadata file for the artwork
    token_json = {
        "name": hospital_input,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash

#Set Theme

over_theme = {'txc_inactive': '#0000FF'}

# Established Patient/Doctor Profiles for Example

patient_1_address = "0x10dfC6C4b40Ff39882E8A107E432305E39dE55d4"
patient_2_address = "0x5e1a5E41F914C1B1498cDFE03E25D23A34239652"
doctor_1_address = "0xbE8DE506e9b48627D5B47703b52E0E8249802a71"
doctor_2_address = "0x1ceA88Ab386170eB43Ecbd4e8b983C5433cAAb25"

d_accounts = [doctor_1_address, doctor_2_address]
p_accounts = [patient_1_address, patient_2_address]

# Creating Webpage

app = hy.HydraApp(
        title='BlocDoc',
        favicon="👨‍⚕️",
        hide_streamlit_markers=True,
        use_banner_images=False,
        use_navbar=True,
        navbar_sticky=False,
        navbar_animation=False,
        navbar_theme=over_theme,
)
@app.addapp(is_home=True)
def Home():
    hy.info('About BlocDoc')
    st.write("BlocDoc is an Electronic Health Record Decentralized Application (EHR-dApp), an etherium-based web application that helps patients and doctors manage electronic health records in a decentralized format. We are trying to apply the EHR systems logic to Blockchain architecture, of course, on a proof of concept level.")
    st.write("Choose an account to get started")
    accounts = w3.eth.accounts
    address = st.selectbox("Select Account", options=accounts)
    st.markdown("---")

@app.addapp()
def Doctor():
    hy.info()
    emr_form = st.container()
    with emr_form:
        with st.form('form1'):
            hospital_input = st.text_input(label='Hospital Name')
            docname_input = st.text_input(label='Doctor Name')
            pat_address = patient_1_address
            record_date = datetime.now().isoformat()
            age_input = st.number_input(label='Age')
            height_input = st.number_input(label='Height in Inches')
            weight_input = st.number_input(label='Weight')
            med_his_notes = st.text_input(label='Notes of Patient Medical History')
            exam_notes = st.text_input(label='Examination Notes')
            dsubmit_button = st.form_submit_button(label='Submit')

            if st.form_submit_button("Create New Patient Chart"):
                chart_ipfs_hash = pin_chart(hospital_input, docname_input, pat_address, record_date, age_input, height_input, weight_input, med_his_notes, exam_notes)

                chart_uri = f"ipfs://{chart_ipfs_hash}"

                tx_hash = contract.functions.registerChart(
                    patient_1_address,
                    chart_uri
                ).transact({'from':doctor_1_address, 'gas':1000000})
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                st.write("Transaction Receipt Mined:")
                st.write(dict(receipt))
                st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
                st.markdown(f"[Chart IPFS Gateway Link](https://ipfs.io/ipfs/{chart_ipfs_hash})")
         st.markdown("---")

@app.addapp()
def Patient():
    hy.info("Get My Medical Records")
    my_token_id = st.number_input(label='Input Id Here')
    if st.button("Click Here"):
        history_filter = contract.events.MedicalDataBank.createFilter(
            fromBlock=0, argument_filters={"tokenID": my_token_id}
        )
        reports = history_filter.get_all_entries()
        if reports:
            for report in reports:
                report_dictionary = dict(report)
                st.markdown("### Medical History Report Log")
                st.write(report_dictionary)
                st.markdown("### Pinata IPFS Report URI")
                report_uri = report_dictionary["args"]["reportURI"]
                report_ipfs_hash = report_uri[7:]
                st.markdown(
                    f"The report is located at the following URI: "
                    f"{report_uri}"
                )
                st.write("You can also view the report URI with the following ipfs gateway link")
                st.markdown(f"[IPFS Gateway Link](https://ipfs.io/ipfs/{report_ipfs_hash})")
                st.markdown("### Medical History Report Log")
                st.write(report_dictionary["args"])



# Functions




app.run()
