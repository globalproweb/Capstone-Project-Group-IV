from datetime import date
import json
import os
from pathlib import Path
from datetime import datetime

import apps
import streamlit as st
from dotenv import load_dotenv
from web3 import Web3
from pinata import *

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))


############################################################################################################################################################################
# Load Contract
############################################################################################################################################################################

load_dotenv("web3.env")

def load_contract():

    # Load ABI
    with open(Path('./contracts/compiled/medrecord.json')) as f:
        contract_abi = json.load(f)

    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


contract = load_contract()

############################################################################################################################################################################
# Helper functions to pin files and json to Pinata
############################################################################################################################################################################


def pin_chart(pat_address, hospital_input, docname_input, age_input, height_input, weight_input, med_his_notes, exam_notes, record_date):

    # Build a token metadata file for the artwork
    pa_file_hash = pin_file_to_ipfs(pat_address)
    hi_file_hash = pin_file_to_ipfs(hospital_input)
    di_file_hash = pin_file_to_ipfs(docname_input)
    ai_file_hash = pin_file_to_ipfs(str(age_input))
    hi_file_hash = pin_file_to_ipfs(str(height_input))
    wi_file_hash = pin_file_to_ipfs(str(weight_input))
    mh_file_hash = pin_file_to_ipfs(med_his_notes)
    en_file_hash = pin_file_to_ipfs(exam_notes)
    rd_file_hash = pin_file_to_ipfs(record_date)

    token_json = {
        "patient": pa_file_hash,
        "hospital": hi_file_hash,
        "doctor": di_file_hash,
        "age": ai_file_hash,
        "height": hi_file_hash,
        "weight": wi_file_hash,
        "medical history": mh_file_hash,
        "exam notes": en_file_hash,
        "record date": rd_file_hash,
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash


# Established Patient/Doctor Profiles for Example

patient_1_address = "0x10dfC6C4b40Ff39882E8A107E432305E39dE55d4"
patient_2_address = "0x5e1a5E41F914C1B1498cDFE03E25D23A34239652"
patient_test_address = "0xc3804461E5BE1D91c8Dc41E0cb26CE30d6654A95"

doctor_1_address = "0xbE8DE506e9b48627D5B47703b52E0E8249802a71"
doctor_2_address = "0x1ceA88Ab386170eB43Ecbd4e8b983C5433cAAb25"

d_accounts = [doctor_1_address, doctor_2_address]
p_accounts = [patient_1_address, patient_2_address, patient_test_address]

# Creating Webpage

def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

def main():
    menu = ['Home', 'Doctor', 'Patient']
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == 'Home':
        st.title("Welcome to BlocDoc")
        st.write("BlocDoc is an Electronic Health Record Decentralized Application (EHR-dApp), an etherium-based web application that helps patients and doctors manage electronic health records in a decentralized format. We are trying to apply the EHR systems logic to Blockchain architecture, of course, on a proof of concept level.")
        st.markdown("---")

    elif choice == 'Doctor':
        st.title("Doctor EMR")
        emr_form = st.container()
        with emr_form:
            with st.form('form1'):
                pat_address = st.selectbox("Select Patient", options=p_accounts)
                hospital_input = st.text_input(label='Hospital Name')
                docname_input = st.text_input(label='Doctor Name')
                age_input = st.number_input(label='Age', step=1)
                height_input = st.number_input(label='Height in Inches', step=1)
                weight_input = st.number_input(label='Weight', step=1)
                med_his_notes = st.text_input(
                    label='Notes of Patient Medical History')
                exam_notes = st.text_input(label='Examination Notes')
                record_date = to_integer(datetime.now())
                dsubmit_button = st.form_submit_button(label='Submit')

                if dsubmit_button:
                    chart_ipfs_hash = pin_chart(pat_address,hospital_input, docname_input, age_input, height_input, weight_input, med_his_notes, exam_notes, record_date)

                    chart_uri = f"ipfs://{chart_ipfs_hash}"

                    tx_hash = contract.functions.setPatientRecord(
                        pat_address,
                        hospital_input,
                        docname_input,
                        age_input,
                        height_input,
                        weight_input,
                        med_his_notes,
                        exam_notes,
                        record_date,
                        chart_uri
                    ).transact({'from': doctor_1_address, 'gas': 1000000})
                    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                    st.write("Transaction Receipt Mined:")
                    st.write(dict(receipt))
                    st.write(
                        "You can view the pinned metadata file with the following IPFS Gateway Link")
                    st.markdown(
                        f"[Chart IPFS Gateway Link](https://ipfs.io/ipfs/{chart_ipfs_hash})")
            st.markdown("---")

    elif choice == 'Patient':
        st.title("Get My Medical Records")
        my_token_id = st.text_input(label='Input Id Here')
        if st.button("Click Here"):
            history_filter = contract.events.SavePatientRecord.createFilter(
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
                    st.write(
                        "You can also view the report URI with the following ipfs gateway link")
                    st.markdown(
                        f"[IPFS Gateway Link](https://ipfs.io/ipfs/{report_ipfs_hash})")
                    st.markdown("### Medical History Report Log")
                    st.write(report_dictionary["args"])

# Functions
main()
