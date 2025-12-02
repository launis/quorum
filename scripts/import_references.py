import re
import requests
import sys

API_URL = "http://localhost:8000"

BIBLIOGRAPHY_TEXT = """
Acemoglu, Daron & Restrepo, Pascual. 2018: The race between man and machine: Implications of technology for growth, factor shares, and employment. American Economic Review, 108(6), 1488–1542. DOI: 10.1257/aer.20160696.
Adadi, Amina & Berrada, Mohammed. 2018: Peeking inside the black-box: A survey on explainable artificial intelligence (XAI). IEEE Access, 6, 52138–52160. DOI: 10.1109/ACCESS.2018.2870052.
AERA, APA & NCME. 2014: Standards for educational and psychological testing. Washington, DC: American Educational Research Association. [Verkkojulkaisu]. Saatavilla: https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf. [Haettu 14.11.2025].
Agrawal, Ajay; Gans, Joshua & Goldfarb, Avi. 2022: Prediction machines: The simple economics of artificial intelligence. Boston: Harvard Business Review Press.
Ahmad, Sultan ym. 2024: A comprehensive review of retrieval-augmented generation (RAG): Key challenges and future directions. arXiv preprint arXiv:2410.12837. DOI: 10.48550/arXiv.2410.12837.
Ahuna, Kelly & Kiener, Michael. 2025: Beyond digital literacy: Cultivating “meta AI” skills in students and faculty. Faculty Focus. Julkaistu 6.8.2025. [Verkkojulkaisu]. Saatavilla: https://www.facultyfocus.com/articles/teaching-with-technology-articles/beyond-digital-literacy-cultivating-meta-ai-skills-in-students-and-faculty/. [Haettu 14.11.2025].
AIMultiple. 2025: 15 Security Threats to LLM Agents (with Real-World Examples). Research AIMultiple. [Verkkojulkaisu]. Saatavilla: https://research.aimultiple.com/security-of-ai-agents/. [Haettu 16.11.2025].
AI Now Institute. 2021: A New AI Lexicon: Function Creep. New York: AI Now Institute. [Verkkojulkaisu]. Saatavilla: https://ainowinstitute.org/publications/collection/a-new-ai-lexicon-function-creep. [Haettu 14.11.2025].
Anderson, Lorin W. & Krathwohl, David R. (toim.). 2001: A taxonomy for learning, teaching, and assessing: A revision of Bloom’s taxonomy of educational objectives. New York: Longman.
Anthropic. 2025a: Constitutional classifiers. Anthropic Policy & Research. [Verkkojulkaisu]. Saatavilla: https://www.anthropic.com/research/constitutional-classifiers. [Haettu 14.11.2025].
Anthropic. 2025b: How we built our multi-agent research system. Anthropic Engineering Blog. Julkaistu 13.6.2025. [Verkkojulkaisu]. Saatavilla: https://www.anthropic.com/engineering/multi-agent-research-system. [Haettu 14.11.2025].
Anthropic. 2025c: Building effective agents. Anthropic Research. [Verkkojulkaisu]. Saatavilla: https://www.anthropic.com/research/building-effective-agents. [Haettu 14.11.2025].
Arcuschin, Iván; Janiak, Jett; Krzyzanowski, Robert; Rajamanoharan, Senthooran; Nanda, Neel & Conmy, Arthur. 2025: Chain-of-Thought Reasoning In The Wild Is Not Always Faithful. arXiv preprint arXiv:2503.08679. DOI: 10.48550/arXiv.2503.08679.
Aryan, Ali & Liu, Zhi. 2025: Causal Reflection with Language Models. arXiv preprint arXiv:2508.04495. DOI: 10.48550/ARXIV.2508.04495.
Auzmor. 2024: How to measure the ROI of AI training programs. Auzmor. [Verkkojulkaisu]. Saatavilla: https://auzmor.com/blog/measure-the-roi-of-ai-training-programs/. [Haettu 14.11.2025].
Bai, Yuntao ym. 2022: Constitutional AI: Harmlessness from AI feedback. arXiv preprint arXiv:2212.08073. DOI: 10.48550/arXiv.2212.08073.
Bareinboim, Elias ym. 2022: On Pearl's hierarchy and the foundations of causal inference. Teoksessa H. Geffner, R. Dechter & J. Halpern (toim.), Probabilistic and causal inference: The works of Judea Pearl. New York: Association for Computing Machinery, 507–556. DOI: 10.1145/3501714.3501743.
Baume, David & Yorke, Mantz. 2002: The reliability of assessment by portfolio on a course to develop and accredit teachers in higher education. Studies in Higher Education, 27(1), 7–25. DOI: 10.1080/03075070120099340.
Bezanilla, María José ym. 2019: Methodologies for teaching-learning in higher education and their relationship with student competences: A systematic review. Educational Research Review, 27, 83–98. DOI: 10.1016/j.edurev.2019.01.004.
Biggs, John B. & Collis, Kevin F. 1982: Evaluating the quality of learning: The SOLO taxonomy (Structure of the Observed Learning Outcome). New York: Academic Press.
Borsboom, Denny; Mellenbergh, Gideon J. & van Heerden, Jaap. 2004: The concept of validity. Psychological Review, 111(4), 1061–1071. DOI: 10.1037/0033-295X.111.4.1061.
Boussioux, Leonard. 2025: Revolutionize quality assurance with AI. Mareana. [Verkkojulkaisu]. Saatavilla: https://mareana.com/whitepaper/qa-playbook/. [Haettu 14.11.2025].
Brennan, Robert L. 2001: Generalizability theory. New York: Springer.
Brooks, Frederick P. 1987: No silver bullet: Essence and accidents of software engineering. Computer, 20(4), 10–19. DOI: 10.1109/MC.1987.1663532.
Bulut, Okan ym. 2024: The Rise of Artificial Intelligence in Educational Measurement: Opportunities and Ethical Challenges. Chinese/English Journal of Educational Measurement and Evaluation, 5(3), Artikla 3. DOI: 10.59863/MIQL7785.
Carolus, Angela ym. 2023: MAILS - Meta AI literacy scale: Development and testing of an AI literacy questionnaire based on well-founded competency models and psychological change- and meta-competencies. arXiv preprint arXiv:2302.09319. DOI: 10.48550/arXiv.2302.09319.
Cemri, M. ym. 2025: Why do multi-agent LLM systems fail? arXiv preprint arXiv:2503.13657. DOI: 10.48550/arXiv.2503.13657.
Center for Innovative Teaching & Learning. 2025: Authentic assessment. Indiana University Bloomington. [Verkkojulkaisu]. Saatavilla: https://citl.indiana.edu/teaching-resources/assessing-student-learning/authentic-assessment/index.html. [Haettu 14.11.2025].
Cheng, Peter C-H. 2001: Scientific discovery, computational models of. Teoksessa N. J. Smelser & P. B. Baltes (toim.), International encyclopedia of the social & behavioral sciences. Amsterdam: Elsevier, 13783–13787. DOI: 10.1016/B978-0-08-097086-8.43085-0.
Cheng, Peter. 2021: Competence assessment by stimulus matching: an application of GOMS to assess chunks in memory. Teoksessa Proceedings of the 19th International Conference on Cognitive Modelling (ICCM 2021). [Verkkojulkaisu]. Saatavilla: https://cidlab.com/files/smp/pb/pb-2021.pdf. [Haettu 14.11.2025].
Chi, Hao ym. 2024: Unveiling causal reasoning in large language models: Reality or mirage? Advances in Neural Information Processing Systems, 37, 96640–96670. DOI: 10.48550/arXiv.2506.21215.
CISA. 2016: Defense in depth. Cybersecurity and Infrastructure Security Agency. [Verkkojulkaisu]. Saatavilla: https://www.cisa.gov/sites/default/files/recommended_practices/NCCIC_ICS-CERT_Defense_in_Depth_2016_S508C.pdf. [Haettu 14.11.2025].
Cohen, Ronald Jay; Swerdlik, Mark E. & Phillips, Sturman M. 1996: Psychological testing and assessment: An introduction to tests and measurement. 3. painos. Mountain View: Mayfield Publishing Company.
Creswell, Antonia ym. 2024: Reducing post-hoc rationalization in large language models. Findings of the Association for Computational Linguistics: ACL 2024, 14757–14771. DOI: 10.18653/v1/2024.findings-acl.867.
Crusius, Timothy W. & Channell, Carolyn E. 2003: The aims of argument: A text and reader. 4. painos. New York: McGraw-Hill.
Cullen, Michael J. 2020: Faking in high-stakes selection: A call to integrate empirical research and applied practice. International Journal of Selection and Assessment, 28(3), 223–226. DOI: 10.1111/ijsa.12289.
D'Angelo, Matt. 2025: AI safety vs AI security in LLM applications: What teams must know. promptfoo. [Verkkojulkaisu]. Saatavilla: https://www.promptfoo.dev/blog/ai-safety-vs-security/. [Haettu 14.11.2025].
David, Jane L. 2019: 15 reasons why standardized tests are problematic. ASCD Blog. [Verkkojulkaisu]. Saatavilla: https://www.ascd.org/blogs/15-reasons-why-standardized-tests-are-problematic. [Haettu 14.11.2025].
de Bruin, Anique B. H.; van Merriënboer, Jeroen J. G. & van Gog, Tamara. 2023: The role of cognitive effort in fostering the acquisition of complex cognitive skills. Teoksessa J. Sweller, J. J. G. van Merriënboer & F. Paas (toim.), Cognitive load theory: A research-based guide to instructional design. Cambridge: Cambridge University Press, 237–256. DOI: 10.1017/9781009403718.011.
Denning, Dorothy E. & Denning, Peter J. 1977: Certification of programs for secure information flow. Communications of the ACM, 20(7), 504–513. DOI: 10.1145/359636.359712.
Der Kiureghian, Armen & Ditlevsen, Ove. 2009: Aleatory or epistemic? Does it matter? Structural Safety, 31(2), 105–112. DOI: 10.1016/j.strusafe.2008.06.020.
Disco. 2024: How to assess the ROI of AI-driven upskilling initiatives. Disco. [Verkkojulkaisu]. Saatavilla: https://www.disco.co/blog/how-to-assess-the-roi-of-ai-driven-upskilling-initiatives. [Haettu 14.11.2025].
Displayr. 2024: Discover the 5 best AI tools for qualitative data analysis. Displayr. [Verkkojulkaisu]. Saatavilla: https://www.displayr.com/discover-the-5-best-ai-tools-for-qualitative-data-analysis/. [Haettu 14.11.2025].
Dreyfus, Stuart E. & Dreyfus, Hubert L. 1980: A Five-Stage Model of the Mental Activities Involved in Directed Skill Acquisition. California Univ Berkeley Operations Research Center. [Verkkojulkaisu]. Saatavilla: https://apps.dtic.mil/sti/pdfs/ADA084551.pdf. [Haettu 18.11.2025].
Du, Yilun ym. 2023: Improving factuality and reasoning in language models through multiagent debate. arXiv preprint arXiv:2305.14325. DOI: 10.48550/arXiv.2305.14325.
Dufner, Michael ym. 2019: Self-enhancement and psychological adjustment: A meta-analytic review. Personality and Social Psychology Review, 23(1), 48–72. DOI: 10.1177/1088868318756467.
Duhem, Pierre. 1906: La théorie physique: son objet et sa structure. Paris: Chevalier & Rivière.
Durlak, Joseph A. & DuPre, Elizabeth P. 2008: Implementation matters: A review of research on the influence of implementation on program outcomes and the factors affecting implementation. American Journal of Community Psychology, 41(3–4), 327–350. DOI: 10.1007/s10464-008-9165-0.
Eloundou, Tyna; Manning, Sam; Mishkin, Pamela & Rock, Daniel. 2023: GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models. arXiv preprint arXiv:2303.10130. DOI: 10.48550/arXiv.2303.10130.
Euroopan komissio. 2024a: The AI Act. Bryssel: Euroopan komissio. [Verkkojulkaisu]. Saatavilla: https://artificialintelligenceact.eu/article/14/. [Haettu 14.11.2025].
Euroopan komission korkean tason asiantuntijaryhmä. 2019: Ethics guidelines for trustworthy AI. Bryssel: Euroopan komissio. [Verkkojulkaisu]. Saatavilla: https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-for-trustworthy-ai. [Haettu 14.11.2025].
Euroopan parlamentti & Euroopan unionin neuvosto. 2024: Euroopan parlamentin ja neuvoston asetus (EU) 2024/1689, annettu 13 päivänä kesäkuuta 2024, tekoälyä koskevista yhdenmukaistetuista säännöistä ja asetusten (EY) N:o 300/2008, (EU) N:o 167/2013, (EU) N:o 168/2013, (EU) 2018/858, (EU) 2018/1139 ja (EU) 2019/2144 sekä direktiivien 2014/90/EU, (EU) 2016/797 ja (EU) 2020/1828 muuttamisesta (tekoälysäädös). Euroopan unionin virallinen lehti, L, 2024/1689. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
Evans, Jonathan St. B. T. & Stanovich, Keith E. 2013: Dual-process theories of higher cognition: Advancing the debate. Perspectives on Psychological Science, 8(3), 223–241. DOI: 10.1177/1745691612460685.
Embretson, Susan E. & Reise, Steven P. 2000: Item response theory for psychologists. Mahwah: Lawrence Erlbaum Associates.
FairTest. 2012: The limits of standardized tests for diagnosing and assisting student learning. FairTest: The National Center for Fair & Open Testing. [Verkkojulkaisu]. Saatavilla: https://fairtest.org/limits-standardized-tests-diagnosing-and-assisting/. [Haettu 14.11.2025].
Federiakin, Denis ym. 2024: Prompt engineering: A new skill for the future of work. Procedia Computer Science, 231, 401–409. DOI: 10.1016/j.procs.2023.12.233.
Festinger, Leon. 1957: A theory of cognitive dissonance. Stanford: Stanford University Press.
Flavell, John H. 1979: Metacognition and cognitive monitoring: A new area of cognitive-developmental inquiry. American Psychologist, 34(10), 906–911. DOI: 10.1037/0003-066X.34.10.906.
Fügener, Andreas; Walzner, Daniel D. & Gupta, Alok. 2025: Roles of Artificial Intelligence in Collaboration with Humans: Automation, Augmentation, and the Future of Work. Management Science. DOI: 10.1287/mnsc.2024.05684.
Ganascia, Jean-Gabriel. 2017: A Popperian falsification of artificial intelligence - Lighthill. arXiv preprint arXiv:1704.08111. DOI: 10.48550/arXiv.1704.08111.
Ganguli, Deep ym. 2022: Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned. arXiv preprint arXiv:2209.07858. DOI: 10.48550/arXiv.2209.07858.
Gao, Luyu ym. 2022: Precise zero-shot dense retrieval without relevance labels. arXiv preprint arXiv:2212.10496. DOI: 10.48550/arXiv.2212.10496.
Goffman, Erving. 1959: The presentation of self in everyday life. New York: Doubleday.
Goodfellow, Ian J. ym. 2014: Generative adversarial networks. Advances in Neural Information Processing Systems, 27, 2672–2680. DOI: 10.48550/arXiv.1406.2661.
Google DeepMind. 2025a: Gemini 3 Pro Model Card. [PDF]. Saatavilla: https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf. [Haettu 14.11.2025].
Google DeepMind. 2025b: Gemini 3 Pro Model Evaluation. [PDF]. Saatavilla: https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_model_evaluation.pdf. [Haettu 14.11.2025].
Google DeepMind. 2025c: Gemini 3: A new era of intelligence. Google Blog. Julkaistu 18.11.2025. [Verkkojulkaisu]. Saatavilla: https://blog.google/products/gemini/gemini-3/. [Haettu 14.11.2025].
Greshake, Kai ym. 2023: Not what you’ve signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. arXiv preprint arXiv:2302.12173. DOI: 10.48550/arXiv.2302.12173.
Guo, Taicheng ym. 2024: Large language model based multi-agents: A survey of progress and challenges. Proceedings of the Thirty-Third International Joint Conference on Artificial Intelligence, 8048–8057. DOI: 10.24963/ijcai.2024/890.
Halpern, Diane F. 2014: Thought and knowledge: An introduction to critical thinking. 5. painos. New York: Psychology Press. DOI: 10.4324/9781315885278.
Hazan, Eric ym. 2024: A new future of work: The race to deploy AI and raise skills in Europe and beyond. McKinsey Global Institute. [Verkkojulkaisu]. Saatavilla: https://www.mckinsey.com/mgi/our-research/a-new-future-of-work-the-race-to-deploy-ai-and-raise-skills-in-europe-and-beyond. [Haettu 14.11.2025].
Hevner, Alan R.; March, Salvatore T.; Park, Jinsoo & Ram, Sudha. 2004: Design Science in Information Systems Research. MIS Quarterly, 28(1), 75–105. DOI: 10.2307/25148625.
Hinton, Geoffrey; Vinyals, Oriol & Dean, Jeffrey. 2015: Distilling the knowledge in a neural network. arXiv preprint arXiv:1503.02531. DOI: 10.48550/arXiv.1503.02531.
Huang, Lei ym. 2023: A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions. ACM Transactions on Information Systems. DOI: 10.1145/3703155.
Hüllermeier, Eyke & Waegeman, Willem. 2021: Aleatoric and epistemic uncertainty in machine learning: an introduction to concepts and methods. Machine Learning, 110, 457–506. DOI: 10.1007/s10994-021-05946-3.
Hume, David. 1739: A Treatise of Human Nature: Being an Attempt to Introduce the Experimental Method of Reasoning into Moral Subjects. Lontoo: John Noon. https://archive.org/details/treatiseofhumann01hume
Hyland, Ken. 2005: Metadiscourse: Exploring interaction in writing. Lontoo: Continuum.
Inan, Hakan ym. 2023: Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations. arXiv preprint arXiv:2312.06674. DOI: 10.48550/arXiv.2312.06674.
ISACA. 2025: 2025 Volume 5 How to measure and prove the value of your AI investments. ISACA. [Verkkojulkaisu]. Saatavilla: https://www.isaca.org/resources/news-and-trends/newsletters/atisaca/2025/volume-5/how-to-measure-and-prove-the-value-of-your-ai-investments. [Haettu 14.11.2025].
ISO/IEC. 2023: Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models (ISO/IEC 25010:2023). Geneve: International Organization for Standardization. [Verkkojulkaisu]. Saatavilla: https://www.iso.org/standard/84727.html. [Haettu 14.11.2025].
Jacobs, Rick; Kafry, Dalia & Zedeck, Sheldon. 1980: Expectations of behaviorally anchored rating scales. Personnel Psychology, 33(3), 595–640. DOI: 10.1111/j.1744-6570.1980.tb00486.x.
Jacovi, Alon & Goldberg, Yoav. 2020: Towards faithfully interpretable NLP systems: How should we define and evaluate faithfulness? Teoksessa Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics. Association for Computational Linguistics, 4198–4205. DOI: 10.18653/v1/2020.acl-main.385.
Jagerman, Rolf ym. 2023: Query expansion by prompting large language models. arXiv preprint arXiv:2305.03653. DOI: 10.48550/arXiv.2305.03653.
Jia, Yihao; Shao, Zenghui; Liu, Yanyi; Jia, Jinyuan; Song, Dawn & Gong, Neil Zhenqiang. 2025: A Critical Evaluation of Defenses against Prompt Injection Attacks. arXiv preprint arXiv:2505.18333. DOI: 10.48550/arXiv.2505.18333.
Johnson, R. Burke & Onwuegbuzie, Anthony J. 2004: Mixed methods research: A research paradigm whose time has come. Educational Researcher, 33(7), 14–26. DOI: 10.3102/0013189X033007014.
Jonsson, Anders & Svingby, Gunilla. 2007: The use of scoring rubrics: Reliability, validity and educational consequences. Educational Research Review, 2(2), 130–144. DOI: 10.1016/j.edurev.2007.05.002.
Kahneman, Daniel. 2011: Thinking, fast and slow. New York: Farrar, Straus and Giroux.
Kiciman, Emre ym. 2023: Causal reasoning and large language models: Opening a new frontier for causality. arXiv preprint arXiv:2305.00050. DOI: 10.48550/arXiv.2305.00050.
Kim, Dong-Gi ym. 2022: Assessing non-technical skills in medical students: An evaluation of the inter- and intra-rater reliability of the behaviorally anchored rating scale (BARS). Teaching and Learning in Medicine, 35(3), 310–319. DOI: 10.1080/10872981.2022.2070940.
Kinicki, Angelo J. ym. 1985: Behaviorally anchored rating scales vs. summated rating scales: Psychometric properties and susceptibility to rating bias. Educational and Psychological Measurement, 45(3), 535–549. DOI: 10.1177/001316448504500310.
Kirshner, Stuart; Klaben, Ben & Dobbe, Sam. 2025: Instruction-Following: The Truth Is In There, But Is It In The Loss? arXiv preprint arXiv:2511.07973. DOI: 10.48550/arXiv.2511.07973.
Klein, Gary. 2007: Performing a Project Premortem. Harvard Business Review, 85(9), 18–19.
Klieger, David M. ym. 2018: Development of the Behaviorally Anchored Rating Scales for the Skills Demonstration and Progression Guide. ETS Research Report Series RR-18-24. Educational Testing Service. DOI: 10.1002/ets2.12210.
Koops, Bert-Jaap. 2021: The concept of function creep. Law, Innovation and Technology, 13(1), 29–56. DOI: 10.1080/17579961.2021.1898299.
Koretz, Daniel M. ym. 1994: The Vermont portfolio assessment program: Findings and implications. Educational Measurement: Issues and Practice, 13(3), 5–16. DOI: 10.1111/j.1745-3992.1994.tb00854.x.
Kreuzberger, Dominik; Kühl, Niklas & Hirschl, Sebastian. 2023: Machine learning operations (MLOps): Overview, definition, and architecture. IEEE Access, 11, 31866–31879. DOI: 10.1109/ACCESS.2023.3262138.
Kruger, Justin & Dunning, David. 1999: Unskilled and unaware of it: How difficulties in recognizing one's own incompetence lead to inflated self-assessments. Journal of Personality and Social Psychology, 77(6), 1121–1134. DOI: 10.1037/0022-3514.77.6.1121.
Lagnado, David A. & Sloman, Steven A. 2006: Time as a guide to cause. Journal of Experimental Psychology: Learning, Memory & Cognition, 32(3), 451–460. DOI: 10.1037/0278-7393.32.3.451.
Lane, Suzanne. 2013: Validity evidence for assessments of higher-order thinking. Journal of Educational Measurement, 50(4), 399–430. DOI: 10.1111/jedm.12028.
Larson, Barbara Z. ym. 2024: Critical thinking in the age of generative AI. Academy of Management Learning & Education, 23(3). DOI: 10.5465/amle.2024.0338.
LeCun, Yann. 2022: A path towards autonomous machine intelligence. OpenReview. [Verkkojulkaisu]. Saatavilla: https://openreview.net/forum?id=BZ5a1r-kVsf. [Haettu 14.11.2025].
Levashina, Julia & Morgeson, Frederick P. 2007: Applicant faking on personality measures: A coping perspective. Academy of Management Review, 32(4), 1118–1136. DOI: 10.5465/amr.2007.26586083.
Levine, Edward L.; Ash, Ronald A. & Bennett, Nathan. 1988: The "behavioral consistency" approach to job analysis: A critical reappraisal. Human Resource Management Review, 8(3), 273–293. DOI: 10.1016/S1053-4822(98)90023-6.
Lewis, Patrick ym. 2020: Retrieval-augmented generation for knowledge-intensive NLP tasks. Advances in Neural Information Processing Systems, 33, 9459–9474. DOI: 10.48550/arXiv.2005.11401.
Li, Feng ym. 2025: An assessment of human–AI interaction capability in the generative AI era: The influence of critical thinking. Journal of Intelligence, 13(6), 62. DOI: 10.3390/jintelligence13060062.
Li, Zhikun ym. 2024: PII-Bench: A benchmark for personally identifiable information (PII) detection and anonymization. arXiv preprint arXiv:2404.03893. DOI: 10.48550/arXiv.2404.03893.
Liang, Tian-Shuo ym. 2023: Encouraging divergent thinking in large language models through multi-agent debate. arXiv preprint arXiv:2305.19118. DOI: 10.48550/arXiv.2305.19118.
Lippi, Marco & Torroni, Paolo. 2016: Argumentation mining: State of the art and emerging trends. ACM Transactions on Internet Technology, 16(2), 1–25. DOI: 10.1145/2850417.
Lison, Pierre ym. 2021: Anonymisation models for text data: State of the art, challenges and future directions. arXiv preprint arXiv:2106.04631. DOI: 10.48550/arXiv.2106.04631.
Liu, Nelson F. ym. 2024: Lost in the middle: How language models use long contexts. Transactions of the Association for Computational Linguistics, 12, 157–173. DOI: 10.1162/tacl_a_00638.
Liu, Xiaogeng ym. 2024: Automatic and universal prompt injection attacks against large language models. arXiv preprint arXiv:2403.04957. DOI: 10.48550/arXiv.2403.04957.
Liu, Yi ym. 2023: Prompt injection attacks and defenses in large language models: A survey. arXiv preprint arXiv:2310.12815. DOI: 10.48550/arXiv.2310.12815.
Luckin, Rosemary ym. 2017: Towards artificial intelligence-based assessment systems. Nature Human Behaviour, 1(3), 0028. DOI: 10.1038/s41562-016-0028.
Ma, Yubo ym. 2024: Mitigating contextual information loss in RAG models through re-ranking. arXiv preprint arXiv:2401.06427. DOI: 10.48550/arXiv.2401.06427.
McHugh, Mary L. 2012: Interrater reliability: the kappa statistic. Biochemia Medica, 22(3), 276–282. DOI: 10.11613/BM.2012.031.
Mesenbrink, Hanna ym. 2025: Orchestrated multi agents sustain accuracy under clinical-scale workloads compared to a single agent. medRxiv. DOI: 10.1101/2025.08.22.25334049.
Messick, Samuel J. 2003: Substance and structure in assessment arguments. Law, Probability and Risk, 2(4), 237–258. DOI: 10.1093/lpr/2.4.237.
Messick, Samuel J. 1989: Validity. Teoksessa R. L. Linn (toim.), Educational measurement. 3. painos. New York: Macmillan, 13–103.
Morgeson, Frederick P.; Delaney-Klinger, Kelly & Hemingway, Monica A. 2007: The importance of job analysis to the legal defensibility of an organization's selection system. Teoksessa L. L. Koppes (toim.), Historical perspectives in industrial and organizational psychology. Mahwah: Lawrence Erlbaum Associates, 301–322.
Moskal, Barbara M. 2000: Scoring rubrics: What, when and how? Practical Assessment, Research, and Evaluation, 7(3). DOI: 10.7275/a5vq-7q66.
Nola, Robert & Sankey, Howard. 2014: Theories of scientific method: An introduction. Lontoo: Routledge. DOI: 10.4324/9781315728666.
Nold, Herbert & Michel, Lukas. 2022: The Dunning-Kruger Effect on Organizational Agility. Academy of Management Proceedings, 2022(1). DOI: 10.5465/AMBPP.2022.10365abstract.
OECD. 2024: Artificial intelligence and the changing demand for skills in the labour market. OECD Artificial Intelligence Papers, No. 14. Paris: OECD Publishing. DOI: 10.1787/88684e36-en.
OpenAI. 2024: OpenAI o1 System Card. OpenAI. [Verkkojulkaisu]. Saatavilla: https://openai.com/index/openai-o1-system-card/. (arXiv preprint arXiv:2412.16720).
OWASP Foundation. 2025a: LLM01:2025 Prompt Injection. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llmrisk/llm01-prompt-injection/. [Haettu 15.11.2025].
OWASP Foundation. 2025b: LLM02:2025 Sensitive Information Disclosure. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
OWASP Foundation. 2025c: LLM05:2025 Improper Output Handling. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
OWASP Foundation. 2025d: LLM06:2025 Excessive Agency. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
OWASP Foundation. 2025e: LLM08:2025 Vector and Embedding Weaknesses. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/. [Haettu 15.11.2025].
OWASP Foundation. 2025f: OWASP Top 10 for Gen AI. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
OWASP Foundation. 2025g: LLM10:2025 Unbounded Consumption. GenAI OWASP Top 10. [Verkkojulkaisu]. Saatavilla: https://genai.owasp.org/llm-top-10/. [Haettu 15.11.2025].
OWASP Foundation. s.a.: Input Validation Cheat Sheet. OWASP Cheat Sheet Series. [Verkkojulkaisu]. Saatavilla: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html. [Haettu 18.11.2025].
Parasuraman, Raja & Riley, Victor. 1997: Humans and automation: Use, misuse, disuse, abuse. Human Factors, 39(2), 230–253. DOI: 10.1518/001872097778543886.
Paulson, F. Leon; Paulson, Pearl R. & Meyer, Carol A. 1991: What makes a portfolio a portfolio. Educational Leadership, 48(5), 60–63.
Pearl, Judea. 2009: Causality: Models, reasoning, and inference. 2. painos. Cambridge: Cambridge University Press. DOI: 10.1017/CBO9780511803161.
Peffers, Ken; Tuunanen, Tuure; Rothenberger, Marcus A. & Chatterjee, Samir. 2007: A Design Science Research Methodology for Information Systems Research. Journal of Management Information Systems, 24(3), 45–77. DOI: 10.2753/MIS0742-1222240302.
Perez, Ethan ym. 2022a: Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned. arXiv preprint arXiv:2209.07858. DOI: 10.48550/arXiv.2209.07858.
Perez, Ethan ym. 2022b: Discovering Language Model Behaviors with Model-Written Evaluations. arXiv preprint arXiv:2212.09251. DOI: 10.48550/arXiv.2212.09251.
Perrow, Charles. 1984: Normal accidents: Living with high-risk technologies. Princeton: Princeton University Press.
Pfeifer, Karen. 2025: Humanity-in-the-loop: Human AI oversight is an imperative. Medium. Julkaistu 22.10.2025. [Verkkojulkaisu]. Saatavilla: https://medium.com/@karenpfeifer/humanity-in-the-loop-human-ai-oversight-is-an-imperative-50bdcc2688d8. [Haettu 14.11.2025].
Polanyi, Michael. 1966: The tacit dimension. Chicago: University of Chicago Press.
Pollitt, Alastair. 2012: The method of Adaptive Comparative Judgement. Assessment in Education: Principles, Policy & Practice, 19(3), 281–300. DOI: 10.1080/0969594X.2012.665354
Popper, Karl. 1934: Logik der Forschung. Vienna: Julius Springer.
PwC. 2024: AI jobs barometer. PricewaterhouseCoopers. [Verkkojulkaisu]. Saatavilla: https://www.pwc.com/gx/en/issues/artificial-intelligence/ai-jobs-barometer.html. [Haettu 14.11.2025].
Quine, Willard Van Orman. 1951: Two dogmas of empiricism. The Philosophical Review, 60(1), 20–43. DOI: 10.2307/2181906.
Raisch, Sebastian & Krakowski, Sebastian. 2021: Artificial intelligence and management: The automation-augmentation paradox. Academy of Management Review, 46(1), 192–210. DOI: 10.5465/amr.2018.0072.
Reinecke, Katharina & Gajos, Krzysztof Z. 2014: Quantifying visual preferences around the world. Proceedings of the SIGCHI Conference on Human Factors in Computing Systems, 717–726. DOI: 10.1145/2556288.2557076.
Sadler, D. Royce. 1989: Formative assessment and the design of instructional systems. Instructional Science, 18(2), 119–144. DOI: 10.1007/BF00117714.
Sagi, Omer & Rokach, Lior. 2018: Ensemble learning: A survey. Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery, 8(4), e1249. DOI: 10.1002/widm.1249.
Saito, Keisuke; Wachi, Akifumi & Akimoto, Youhei. 2023: Verbosity bias in preference labeling by large language models. arXiv preprint arXiv:2310.10864. DOI: 10.48550/arXiv.2310.10864.
Saltzer, Jerome H. & Schroeder, Michael D. 1975: The protection of information in computer systems. Proceedings of the IEEE, 63(9), 1278–1308. DOI: 10.1109/PROC.1975.9939.
Sgaier, Sema K. ym. 2020: The case for causal AI. Stanford Social Innovation Review, 18(3), 50–55. DOI: 10.48558/KT81-SN73.
Shafiyeva, Ulviyya. 2021: Assessing Students' Minds: Developing Critical Thinking or Fitting into Procrustean Bed. European Journal of Education, 4(2), 78–91. DOI: 10.26417/452bxv17s.
Sharma, Mrinank ym. 2025: Constitutional classifiers: Defending against universal jailbreaks across thousands of hours of red teaming. arXiv preprint arXiv:2501.18837. DOI: 10.48550/arXiv.2501.18837.
Shavelson, Richard J. 2010: On the measurement of competency. Empirical Research in Vocational Education and Training, 2(1), 41–63.
Shaffer, David Williamson; Collier, Wesley & Ruis, A. R. 2016: A tutorial on Epistemic Network Analysis: Analyzing the structure of connections in cognitive, social, and interaction data. Journal of Learning Analytics, 3(3), 9–45. DOI: 10.18608/jla.2016.33.3.
Shavelson, Richard J. 2013: On an approach to testing and modeling competence. Educational Psychologist, 48(2), 73–86. DOI: 10.1080/00461520.2013.779483.
Shen, Yongliang ym. 2023: Large Language Models as Tool Makers. arXiv preprint arXiv:2305.17126. DOI: 10.48550/arXiv.2305.17126.
Shinn, Noah ym. 2023: Reflexion: an autonomous agent with dynamic memory and self-reflection. arXiv preprint arXiv:2303.11366. DOI: 10.48550/arXiv.2303.11366.
Shuster, Kurt ym. 2021: Retrieval augmentation reduces hallucination in conversation. arXiv preprint arXiv:2104.07567. DOI: 10.48550/arXiv.2104.07567.
Silva, Bruno ym. 2025: Development of an Adapted Version of the Motor Competence Assessment (MCA) for Older Adults. Journal of Clinical Medicine, 14(21), 7866. DOI: 10.3390/jcm14217866.
Smith, Patricia Cain & Kendall, Lorne M. 1963: Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales. Journal of Applied Psychology, 47(2), 149–155. DOI: 10.1037/h0047060.
Strathern, Marilyn. 1997: 'Improving ratings': audit in the British university system. European Review, 5(3), 305–321. DOI: 10.1002/(SICI)1234-981X(199707)5:3<305::AID-EURO184>3.0.CO;2-4.
Stumborg, Michael F. ym. 2022: Goodhart's law: Recognizing and mitigating the manipulation of measures in analysis. CNA Occasional Paper. [Verkkojulkaisu]. Saatavilla: https://www.cna.org/reports/2022/09/Goodharts-Law-Recognizing-Mitigating-Manipulation-Measures-in-Analysis.pdf. [Haettu 14.11.2025].
Supianto, Arief Andy ym. 2023: A systematic review of multi-agent systems in educational assessment. Computers & Education: Artificial Intelligence, 4, 100135. DOI: 10.1016/j.caeai.2023.100135.
Suskie, Linda. 2009: Assessing student learning: A common sense guide. 2. painos. San Francisco: Jossey-Bass.
Talboy, Alisha & Fuller, Elizabeth. 2023: Large language models show humanlike cognitive biases. arXiv preprint arXiv:2308.14343. DOI: 10.48550/arXiv.2308.14343.
Tétard, Franck & Collan, Mikael. 2009: Lazy User Theory: A Dynamic Model to Understand User Selection of Products and Services. Proceedings of the 42nd Hawaii International Conference on System Sciences, 1–10. Waikoloa, HI: IEEE Computer Society. DOI: 10.1109/HICSS.2009.290
Toulmin, Stephen E. 2003: The uses of argument. Päivitetty painos. Cambridge: Cambridge University Press. DOI: 10.1017/CBO9780511802031.
Towards AI. 2025: AI Sandbox in 2025: How Enterprises and Governments Shape AI's Future. Towards AI. Julkaistu 26.9.2025. [Verkkojulkaisu]. Saatavilla: https://pub.towardsai.net/ai-sandbox-in-2025-how-enterprises-and-governments-shape-ais-future-b41f0d267c4d. [Haettu 14.11.2025].
Trivedi, Harsh ym. 2024: Interleaving retrieval with chain-of-thought reasoning for knowledge-intensive multi-step questions. arXiv preprint arXiv:2401.10133. DOI: 10.48550/arXiv.2401.10133.
Turpin, Miles ym. 2023: Language models don't always say what they think: Unfaithful explanations in chain-of-thought prompting. Teoksessa A. Oh, T. Hashimoto & D. Blei (toim.), Advances in Neural Information Processing Systems 36. La Jolla: Neural Information Processing Systems Foundation, 21016–21033.
Turpin, Miles ym. 2025: Executable counterfactuals: Improving LLMs' causal reasoning through code. arXiv preprint arXiv:2510.01539. DOI: 10.48550/arXiv.2510.01539.
Tutkimuseettinen neuvottelukunta TENK. 2019: Ihmiseen kohdistuvan tutkimuksen eettiset periaatteet ja ihmistieteiden eettinen ennakkoarviointi Suomessa. Tutkimuseettisen neuvottelukunnan ohje 2019. Tutkimuseettisen neuvottelukunnan julkaisuja 3/2019. Helsinki: TENK. [Verkkojulkaisu]. Saatavilla: https://tenk.fi/sites/default/files/2021-01/Ihmistieteiden_eettisen_ennakkoarvioinnin_ohje_2020.pdf. [Haettu 14.11.2025].
Tversky, Amos & Kahneman, Daniel. 1974: Judgment under uncertainty: Heuristics and biases. Science, 185(4157), 1124–1131. DOI: 10.1126/science.185.4157.1124.
W3C. 2008: Migrating to Unicode. W3C Internationalization (I18n) Activity. [Verkkojulkaisu]. Saatavilla: https://www.w3.org/International/articles/unicode-migration/. [Haettu 14.11.2025].
Wachsmuth, Henning ym. 2017: Computational argumentation quality assessment in natural language. Proceedings of the 15th Conference of the EACL, 176–187. DOI: 10.18653/v1/E17-1017.
Walton, Douglas N.; Reed, Chris & Macagno, Fabrizio. 2008: Argumentation schemes. Cambridge: Cambridge University Press. DOI: 10.1017/CBO9780511802034.
Wang, Yuxia ym. 2023: A survey on an authoritarian bias: The blind spot of large language models. arXiv preprint arXiv:2312.06086. DOI: 10.48550/arXiv.2312.06086.
Wang, Xuezhi; Wei, Jason; Schuurmans, Dale; Le, Quoc; Chi, Ed; Narang, Sharan; Chowdhery, Aakanksha & Zhou, Denny. 2022: Self-Consistency Improves Chain of Thought Reasoning in Language Models. arXiv preprint arXiv:2203.11171. DOI: 10.48550/arXiv.2203.11171
Weidinger, Laura ym. 2021: Ethical and social risks of harm from language models. arXiv preprint arXiv:2112.04359. DOI: 10.48550/arXiv.2112.04359.
Weston, Jason & Sukhbaatar, Sainbayar. 2023: System 2 attention (is something you might need too). arXiv preprint arXiv:2311.11829. DOI: 10.48550/arXiv.2311.11829.
Wiggins, Grant. 1998: Educative assessment: Designing assessments to inform and improve student performance. San Francisco: Jossey-Bass.
Wisse, Gerben & Greve, Rutger. 2023: AI in educational assessment: A systematic review of formative and summative applications. Computers & Education: Artificial Intelligence, 5, 100174. DOI: 10.1016/j.caeai.2023.100174.
Wolf, Kenneth & Stevens, Ellen. 2007: The role of rubrics in advancing and assessing student learning. The Journal of Effective Teaching, 7(1), 3–14.
Wolf, Yotam ym. 2023: Fundamental Limitations of Alignment in Large Language Models. arXiv preprint arXiv:2304.11082. DOI: 10.48550/arXiv.2304.11082.
Wolters Kluwer. 2024: 2024 Future ready lawyer survey report. [Verkkojulkaisu]. Saatavilla: https://www.wolterskluwer.com/en/know/future-ready-lawyer-2024. [Haettu 14.11.2025].
Wooldridge, Michael. 2009: An introduction to multiagent systems. 2. painos. Chichester: John Wiley & Sons.
World Economic Forum. 2023: Future of Jobs Report 2023. [Verkkojulkaisu]. Saatavilla: https://www.weforum.org/publications/the-future-of-jobs-report-2023/. [Haettu 18.11.2025].
Wu, Junjie ym. 2024: Large Language Models are Challenged by an Abundance of Over-complicated Instructions. arXiv preprint arXiv:2409.07844. DOI: 10.48550/arXiv.2409.07844.
Wynn, Alexander; Satija, Harsh & Hadfield, Gillian. 2025: Talk isn't always cheap: Understanding failure modes in multi-agent debate. Proceedings of the ICML 2025 Workshop on Multi-Agent Systems. arXiv preprint arXiv:2509.05396. DOI: 10.48550/arXiv.2509.05396.
Ye, Rui ym. 2025: X-MAS: A comprehensive testbed for evaluating heterogeneous LLM-driven multi-agent systems. arXiv preprint arXiv:2505.16997. DOI: 10.48550/arXiv.2505.16997.
Yeager.ai. 2023: AI Agent Kryptonite - Prompt Saturation and Context Bleeding. Medium. Julkaistu 16.10.2023. [Verkkojulkaisu]. Saatavilla: https://medium.com/yeagerai/ai-agent-kryptonite-prompt-saturation-and-context-bleeding-4db7c4329e4e. [Haettu 16.11.2025].
Yi, Zhaoyang ym. 2025: Benchmarking and defending against indirect prompt injection attacks on large language models. arXiv preprint arXiv:2312.14197. DOI: 10.48550/arXiv.2312.14197.
Zhang, Yunhua ym. 2024: Soar: The Future of AI-Driven Architectures through Directed Acyclic Graph Reasoning. arXiv preprint arXiv:2404.05678. DOI: 10.48550/arXiv.2404.05678.
Zilliz. 2024: Ensuring Secure and Permission-Aware RAG Deployments. Zilliz Blog. [Verkkojulkaisu]. Saatavilla: https://zilliz.com/blog/ensure-secure-and-permission-aware-rag-deployments. [Haettu 14.11.2025].
Zou, Wei; Geng, Runpeng; Wang, Binghui & Jia, Jinyuan. 2024: PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models. arXiv preprint arXiv:2402.07867. DOI: 10.48550/arXiv.2402.07867.
"""

def parse_and_import():
    # Split by newline
    lines = BIBLIOGRAPHY_TEXT.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. Extract Author(s) and Year for Short Citation
        # Regex to find Year (4 digits followed by colon or dot)
        # Example: "Acemoglu, Daron & Restrepo, Pascual. 2018:"
        
        # Try to find the year pattern
        match = re.search(r'(\d{4})[:\.]', line)
        if match:
            year = match.group(1)
            # Everything before the year is roughly the author part
            author_part = line[:match.start()].strip()
            # Remove trailing dot if present
            if author_part.endswith('.'):
                author_part = author_part[:-1]
                
            # Construct Short Citation
            # Simplify author part for short citation? 
            # E.g. "Acemoglu, Daron & Restrepo, Pascual" -> "Acemoglu & Restrepo"
            # "AERA, APA & NCME" -> "AERA, APA & NCME"
            # "Ahmad, Sultan ym." -> "Ahmad ym."
            
            # Simple heuristic: Split by comma, take first word of first part?
            # Or just use the whole author part if it's short enough?
            # Let's try to be smart.
            
            short_author = author_part
            
            # Handle "Surname, Firstname" format
            # If there are semicolons, it's a list of authors: "Agrawal, Ajay; Gans, Joshua..."
            if ';' in author_part:
                authors = author_part.split(';')
                first_author = authors[0].split(',')[0].strip()
                if len(authors) > 1:
                    short_author = f"{first_author} ym."
                else:
                    short_author = first_author
            elif '&' in author_part:
                # "Acemoglu, Daron & Restrepo, Pascual"
                parts = author_part.split('&')
                # Extract surnames
                surnames = []
                for p in parts:
                    if ',' in p:
                        surnames.append(p.split(',')[0].strip())
                    else:
                        surnames.append(p.strip())
                short_author = " & ".join(surnames)
            elif ',' in author_part:
                 # "Wiggins, Grant" -> "Wiggins"
                 # But "AERA, APA & NCME" has commas too.
                 # Check if it looks like "Surname, Firstname"
                 first_part = author_part.split(',')[0]
                 if " " not in first_part: # Likely a surname
                     short_author = first_part
                 else:
                     # Maybe organization name? Keep as is or truncate?
                     # Let's keep it simple: if it contains "ym.", keep it.
                     if "ym." in author_part:
                         short_author = author_part.split(',')[0] + " ym."
            
            short_citation = f"({short_author} {year})"
            
            # Construct ID
            # REF_AUTHOR_YEAR
            safe_author = re.sub(r'[^a-zA-Z0-9]', '_', short_author).upper()
            safe_author = re.sub(r'_+', '_', safe_author).strip('_')
            # Limit length
            safe_author = safe_author[:20]
            
            comp_id = f"REF_{safe_author}_{year}"
            
            # Check if exists (optional, but good practice)
            # For now, just try to create.
            
            payload = {
                "id": comp_id,
                "name": f"Ref: {short_author} {year}",
                "type": "Reference",
                "description": f"Reference entry for {short_author} {year}",
                "content": f"Reference: {short_citation}", # Dummy content, real value is in citation fields
                "citation": short_citation,
                "citation_full": line,
                "module": "references",
                "component_class": "ReferenceComponent"
            }
            
            print(f"Importing: {comp_id} -> {short_citation}")
            
            try:
                res = requests.post(f"{API_URL}/config/components", json=payload)
                if res.status_code == 200:
                    print("  -> Success")
                else:
                    print(f"  -> Failed: {res.text}")
            except Exception as e:
                print(f"  -> Error: {e}")

if __name__ == "__main__":
    parse_and_import()
