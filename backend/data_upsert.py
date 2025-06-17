import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger
from dotenv import load_dotenv

class RAGManager:
    def __init__(self, working_dir="./rag_storage"):
        setup_logger("lightrag", level="INFO")
        self.working_dir = working_dir
        if not os.path.exists(working_dir):
            os.mkdir(working_dir)
        
        self.rag = None

    async def initialize(self):
        """Initialize the RAG system asynchronously"""
        self.rag = LightRAG(
            working_dir=self.working_dir,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_complete,
        )
        
        # Initialize storage and pipeline status
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
        
        # # Ensure pipeline status has required fields
        # pipeline_status = self.rag.get_pipeline_status()
        # if "history_messages" not in pipeline_status:
        #     pipeline_status["history_messages"] = []
        # if "processing_queue" not in pipeline_status:
        #     pipeline_status["processing_queue"] = []
        # if "processed_documents" not in pipeline_status:
        #     pipeline_status["processed_documents"] = []
        
        return self.rag

    async def insert(self, text):
        """Insert text into the RAG system"""
        if not self.rag:
            await self.initialize()
        
        # Create a new event loop for the insert operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            await self.rag.ainsert(text)
        finally:
            loop.close()

async def main():
    # Sample data to insert
    data = """
    [HEADER] Level: H1 Text: Frequently Asked Questions\n\n[CONTENT] \nWith the intention of providing more 
    clarity on different practices and policies of Technovert to all the employees, this document has been designed 
    and is expected to be referred as a firsthand document for clarity on the following domains:\n\nA. ATTENDANCE B. 
    LEAVE C. PAYROLL D. INSURANCE E. ID CARDS F. MEAL CARDS \nG. ONBOARDING H. TIMESHEETS I. GENERAL QUERIES J. 
    EMPLOYEE RELIEVING\n\n[HEADER] Level: H2 Text: A. ATTENDANCE\n\n[LIST] \n1. What is my attendance tracking policy?
    \n   - Your attendance tracking policy will give you information on late arrival, work hours, missing swipes. You 
    can refer to it at this link, https://technovert.keka.com/#/me/attendance\n   \n2. I have missed my swipe, can HR 
    or my manager adjust it?\n   - You can find the attendance tracking policy, for the number of missing swipes you 
    are eligible for in a week. Beyond that limit, you cannot regularize the missing swipes and for HR to adjust it, 
    you need to seek approval from your manager, and then the HR manager can adjust it accordingly.\n\n3. What is the 
    attendance cycle?\n   - The attendance cycle is same as payroll cycle and starts from Previous month’s 26th to 
    current month’s 25th.\n\n4. What is the last day to get the leave days regularized?\n   - Since the payroll cycle 
    is same as attendance cycle and salary processing starts by 27th, you have to get all the approvals and missing 
    swipes adjusted before 27th.\n\n5. How are Work from Home requests approved?\n   - The Work from Home requests get 
    automatically approved in the Keka portal after an employee applies them. However, if you face any issues please 
    contact the HR team immediately.\n\n6. How to record my attendance if I go to Keka office?\n   - In a case when 
    you are visiting Keka on a frequent basis, you can request your manager to add you to Keka attendance tracking 
    policy or if it is on adhoc/rare basis then you can accordingly request the HR to adjust them for the day.[HEADER] 
    Level: H2 Text: B. LEAVE\n\n[CONTENT] \n11. What is my leave policy & leave accrual policy?\n\nThe leave policy 
    can be checked at https://technovert.keka.com/#/me/leaves. By clicking on “Leave Policy Explanation” in the leaves 
    section, you can see the accrual, application restrictions, leave restrictions, leave lapse etc.\n\n12. What is 
    the policy of work from home? How many am I eligible for?\n\nWork from Home can be availed by all the employees 
    apart from freshers or anyone with <2.5 years experience.\nIn case you are eligible there will be a button that 
    pops to the right of the screen in Attendance section https://technovert.keka.com/#/me/attendance. By default, WFH 
    is eligible to be availed twice a month.\n\n13. My Salary did not get credited?\n\nThere are couple of reasons why 
    your salary did not get credited, like,\n\n[LIST]\n    a. You haven’t submitted your bank details in KEKA\n    b. 
    The details are not verified by HR\n    c. The bank account is not activated\n    d. You provided incorrect 
    details\n\nPlease talk to HR to know the exact reason, and to address the issue\n\n14. How many missing swipes & 
    late arrivals are allowed in a month?\n\nThe Missing swipes and late arrivals are mentioned exclusively in your 
    Attendance Tracking Policy, it can be checked in the below link. https://technovert.keka.com/#/me/attendance.
    \n\n15. My leave got deducted due to exceeding missing swipes? What should I do?\n\nIn case you have missed your 
    swipes due to fault in the attendance machine, it will be automatically adjusted by machine reset.\n\nIn case it 
    is because you have forgotten to swipe, then you can regularize yourself to the number of times as indicated in 
    the attendance tracking policy assigned to you, beyond this you need to get in touch with your HR.\n\n[CONTENT] 
    \n7. What is the Week-off policy for trainees?\n\nFor all the trainees the training period is for 6 months, and it 
    might get extended to a max of 3 months until which the week-offs will be restricted to only Sundays. Once 
    confirmed they can avail Saturday & Sunday as weekly off. You can check what has been allotted to you by going to 
    Assigned Timings section in https://technovert.keka.com/#/me/attendance\n\n8. What if I arrive late to office?
    \n\nAs per your attendance tracking policy, you can check the grace period and late arrival penalty. https://
    technovert.keka.com/#/me/attendance[LIST] \n16. My leave got deducted due to exceeding late arrivals? What should 
    I do?\n   In this case you need to drop a mail to your reporting manager, who will approve/reject your request, on 
    basis of which HR can adjust the attendance records.\n\n17. Can I change my leave type?\n   You can change your 
    leave type any time before it is approved, and it cannot be done post that. You need to drop a mail to your 
    reporting manager and HR to get it done.\n\n18. I need an emergency leave, but do not have leave balance, what to 
    do?\n   In such cases keep your manager informed on the number of days and the purpose of the leave, so that 
    adequate planning can be done within the team.\n\n[HEADER] Level: H1 Text: C. PAYROLL\n[LIST] \n19. What is the 
    payroll cycle? (Salary effective date to be included)\n   The payroll cycle is between 26th of the previous month 
    to 25th of the current month.\n\n20. Who handles payroll/tax related issues?\n   Our Finance representative will 
    be the single point of contact for these issues.<indiapayroll@technovert.com>\n\n21. Where should I check my 
    payslip?\n   You can check your payslip here https://technovert.keka.com/#/finances/mypay/payslips\n\n22. My pay 
    has got increased but it didn’t reflect in my pay slip or the salary for the month. Why?\n   This is a rare case 
    of inconvenience, but it might be because of a couple of reasons like,\n   a. The input was not acknowledged by 
    the Finance representative\n   b. The effective date of the pay is changed Connect to your HR to know the exact 
    reason of the issue.\n\n23. My pay slip shows a different amount from what is paid. What could be the reason?\n   
    This usually happens in the cases of Appraisal, where in the effective date of payment can be anywhere in the mid 
    of the payroll cycle. You can check the effective date of revised pay at https://technovert.keka.com/#/finances/
    mypay/salary\n\n24. Where should I declare my tax declarations?\n   You can declare your taxes under “Manage Tax” 
    section in the below link. \n   https://technovert.keka.com/#/finances/summary\n\n25. How to claim reimbursement?
    \n   You can claim for reimbursement under the “Standard Expense Policy”. Check this under Time & Attendance tab 
    by going to Job section of your profile. https://technovert.keka.com/#/me/job[HEADER] Level: H1 Text: D. 
    INSURANCE\n\n[CONTENT] \n26. What is the maximum limit for reimbursements?\nThe limit for reimbursements differs 
    for each category:\n\n[LIST] \n- Business Travel – The per diem allowance is a daily allowance for your business 
    travel expenses. It includes lodging, meals and incidentals.\n- Relocation Expenses – This includes travel/
    accommodation expenses during relocation, as a part of your onboarding expense.\n\nPlease refer to the Travel 
    Policy Document for more info.\n\n27. I need form 16. Where can download it from?\nYou need to drop a mail to 
    Finance Executive, as for now we don’t have such feature. (check your official mail id for every FY)\n\n28. My 
    name is not correct in the PF account/pay slip. How to correct it?\nThe process of data correction for EPF account 
    is completely automated, and you can do profile corrections through https://unifiedportal-mem.epfindia.gov.in/
    memberinterface/\n\nYou can also change your mobile number, email id, DOB if you want to.\n\nName in the pay slip 
    is in the format of <FirstName> <Last Name> as mentioned in your KEKA Profile, if you wish to change contact 
    Finance Rep.\n\n29. Where can I find my UAN number?\nYou can check your UAN and PF number on your pay slip that 
    gets generated after salary credit each month.\n\n30. What is the medical insurance policy?\nPlease find the 
    policy in the link hereby, https://technovert.keka.com/#/employees/documents/organization\n\nThe scheme provides 
    coverage for self, spouse and 2 kids. For further details get in touch with your HR.\n\n31. My/My family insurance 
    details are updated but I dint receive any Health Insurance Card. When can I expect? \nThe health insurance 
    provider will require 30-45 days of time to provide the Health Insurance Cards, however an E card can be provided 
    immediately.\n\nFor further details get in touch with your HR.\n\n32. I have some hospitalization/medical charges 
    to be covered for me/my family, how should I claim insurance for the same?\nFor understanding the claim 
    submissions, please visit https://technovert.keka.com/#/employees/documents/organization\n\n[FIGURE] There is a 
    logo for Technovert with the slogan \"TECHIE BY NATURE\" in the upper right corner of the page.[HEADER] Level: H1 
    Text: TECHNOVER TECHIE BY NATURE\n\n[CONTENT] \n33. How should I register a new family member for the Insurance 
    policy?\nIn case you are newly married or have newborns in your family then you must report the same immediately 
    to HR to include their details for the Health Insurance Policy to, else it will be postponed till the next FY.
    \n\n34. Who all are eligible for coverage under Medical Insurance Policy?\nPlease go through the policy guidelines 
    in the link hereby, https://technovert.teka.com/#/employees/documents/organization\n\n35. What is the amount to be 
    paid for Medical Insurance?\nIt is a company sponsored Health Insurance Policy, hence your out-of-pocket cost 
    remains zero.\n\n36. Can I extend my insurance benefit to my parents?\nCurrently it is a Group policy with 1+3 
    coverage (self + spouse & 2 kids) hence benefits cannot be extended to parents.\n\n37. Can I extend the coverage 
    amount of my medical insurance?\nYes, based on your designation and approval from Management, you can drop a 
    request with the HR in that case for more information.\n\n[HEADER] Level: H2 Text: E. ID CARDS\n\n[CONTENT]\n38. 
    My card is not registering attendance, how to resolve this issue?\nThere are couple of reasons for this issue to 
    come up\n  a. Problem with the machine\n  b. Card deactivated \nPlease notify both IT admin and HR to resolve the 
    issue.\n\n39. What to be done If I lose/misplace/forget my id card?\nIn this case, please follow the procedure as 
    indicated in the below link https://technovert.teka.com/#/employees/documents/organization\n\n40. What is the card 
    reissuance fees?\nIn case of loss of ID card, you need to pay a reissuance fees of INR 200/-.\n\n[HEADER] Level: 
    H2 Text: F. MEAL CARDS\n\n[CONTENT]\n41. I am unable to access my meal card. What could be the reason?\nThis might 
    be because of no balance, or the merchant is not registered with the meal card service provider.\n\n42. I have 
    exceeded my limit in the Meal Card Balance. What should I do?\nThe maximum limit in the meal card is 10,000/- 
    beyond which the credit would be reject because of\n\n[LIST] \n- Problem with the machine\n- Card deactivated \n\n
    [FIGURE] None in the document.```plaintext\n[HEADER] Level: G Text: ONBOARDING\n[CONTENT] \n44. By when should I 
    complete the profile information in Keka?\nPlease update your profile within a week of joining.\n\n45. I am unable 
    to upload documents in Keka.\nYou will face this issue in case you have already uploaded one and trying to 
    reupload to rewrite the existing file. Kindly ask your HR to delete the existing one, so that you can upload it 
    afresh.\n\n46. I am unable to edit the documents I have updated in Keka.\nYou can edit the documents only until 
    verification. Once the document is verified by HR, you cannot upload another document in its place. For this, 
    please ask your HR to delete it, stating a relevant reason and you can upload post that.\n\n47. Where should I 
    upload my bank details for salary credit?\nYou have to upload the “First page of the cheque book” after your 
    account is created with our registered bank partners, by going to Payroll KYC tab in this link https://technovert.
    keka.com/#/employees/documents/organization\n\n48. How should I claim my travel and accommodation expenses at the 
    time of joining/or any other business travel?\nIn this case, ask your HR to assign you an expense policy.\n\n49. I 
    haven’t received my ID card. When will I receive it?\nProcessing ID card is not inhouse and the vendor takes min 
    of 10-15 days to process the cards. Your HR will keep you posted on this.\n\n[HEADER] Level: H Text: TIMESHEETS\n
    [CONTENT] \n50. What is the purpose of timesheets?\nThis is to track the time spent by employee on several tasks 
    assigned to him.\n\n51. Where should I check my timesheets?\nYou can check that in this link -> https://technovert.
    keka.com/#/me/timesheets/all\n```\n\nThere were no tables, lists, or important figures/diagrams found in the 
    provided document page.[CONTENT]  \n52. When should I update my timesheets in a month?  \nTimesheets should be 
    updated daily.  \n\n53. I am unable to view my timesheets. What is to be done?  \nAsk your HR to enable timesheets 
    option for you.  \n\n[HEADER] Level: H1 Text: I. GENERAL INQUIRIES  \n\n54. What is the preferred mode of 
    communication?  \nMicrosoft Teams is preferred, however for official and confidential communication we recommend 
    using Microsoft Outlook to better organize your work and have healthy work discussions.  \n\n55. Can I take loan 
    for personal purposes? If so, what is the loan issue and repayment policy?  \nFor employees’ benefit you have the 
    provision of availing loan at 0% interest. For the guidelines on availing and repaying, please refer to this 
    annexure.  \nhttps://technovert.keka.com/#/employees/documents/organization  \n\n[HEADER] Level: H1 Text: J. 
    EMPLOYEE RELIEVING  \n\n56. How should I submit my resignation & what formalities should I perform?  \nYou can 
    drop your resignation over mail to your reporting manager, marking HR and Department Head in CC. Further 
    formalities will be reverted over the same mail from the HR.  \n\n57. What is my notice period?  \nNotice Period 
    for your role will be as per the Terms & Conditions mentioned in your Appointment Letter.  \n\n58. What documents 
    will I be receiving as part of my Full & Final Settlement?  \nPost your relieving from the services of Technovert, 
    you will receive the following documents.  \n\n[LIST]  \na) Relieving & Experience Letter  \nb) Full & Final 
    Statement  \nc) Form 16 & Form 12BB  \n\n59. What will my Relieving/Experience certificate consist of?  \nThis 
    document indicates your,  \n\n[LIST]  \na) Basic Employment details (Name, Emp Id, DOJ, Designation)  \nb) No. of 
    years of service  \nc) Relieving Date  \n\n60. When will I get my Full & Final pay?  \nYour F&F settlements start 
    once all the assets are procured and after clearing any outstanding loans. You would be getting this typically in 
    the end of payroll cycle you have exited.[HEADER] Level: H3 Text: 61. When will I get my Relieving documents & 
    Form 16?\n[CONTENT] Relieving documents will be couriered to you 2 weeks from the “Last working date”. Form 16 
    will be mailed in the month of June in the upcoming Financial year. E.g. if your relieving is in Jan 2019, you’ll 
    get your Form 16 by June 2019.\n\n[HEADER] Level: H3 Text: 62. How can I avail my Leave in notice period?\n
    [CONTENT] You will not be allowed to take anymore Privileged Leave; however, you can consume the pending Sick/
    Casual Leave.\n\n[HEADER] Level: H3 Text: 63. What is the knowledge transfer plan?\n[CONTENT] Post confirmation of 
    your resignation, your manager will inform you on the Knowledge Transfer schedule to your successor.\n\n[FIGURE] 
    Description: A logo of Technovert with the tagline \"TECHIE BY NATURE\" is displayed at the top right corner of 
    the page.
    """
    
    # Initialize and insert data
    query = "What is my payroll cycle?"
    rag_manager = RAGManager()
    await rag_manager.initialize()
    # await rag_manager.insert(data)
    response = await rag_manager.rag.aquery(query, param=QueryParam(mode="naive"))
    print(response)
    # print("Data successfully inserted into RAG system")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())