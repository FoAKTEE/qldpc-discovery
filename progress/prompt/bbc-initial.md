**central tasks**
* https://arxiv.org/abs/2606.02418 this is the holly grail of this project: WE WANT TO WRITE A CODE BASE AND A PIPELINE TO REPEAT THIS PROCESS OF AUTO-DISCOVERY!!!
* final product: code base, pipeline, and a timeline of code results discovery

* this is our main working folder, you should audit it in detail and use phys-agentic-loop/0-source-import pipeline's method to extract the file logical dependency, and also theorem logical dependency
* [https://arxiv.org/abs/2002.08953  ](https://arxiv.org/abs/2606.02418)download tex file to ref-paper, run phys-agentic-loop/0-source-import pipeline on this tex file and these are proof targets; 
* git commit to bbc branch

**management strategy** 
* Audit `.claude` and `phys-agentic-loop` and modify their content to accommodate this task; turn on the ralph loop.
* audit the repo before the start; audit the repo after paper decomposition -> check for reusable scripts!!!
* Each substage must be documented, committed, not pushed to GitHub (commit after substage progress!).
* Each iteration must update `phys-agentic-loop/notes/*` to keep multi-timescale tracking current.
* Read `phys-agentic-loop/alignment.md` and always keep MUSK mode on!!!
* Initial step: merge `phys-agentic-loop/code_quality_policy.md` into the pipeline.
* If an ingredient does not exist, run escalation (`pipelines/6-escalation`) to find detailed,
  high-citation references; download the PDF (use an agentic team locally to convert it to tex) or
  the tex directly, and run decomposition on it to build a guided knowledge base.

**phys-agentic-loop**
* self-propmt only every 5 to 10 1m-context window, during this long multi-iteration run, self-prompting of the phys-agentic-loop is turned off
* use ultracode workflow


**SELF-EVOLUTION**
* escalation: inject to infra: you are ALLOWED and ENCOURAGED to search for useful paper and code and download to ref-paper and ref-code; run decomposition
* self-evolution and self-correction of .claude and phys-agenticloop every 5-10 1m-context window 1. selfprompting and 2. phys-agentic-loop to optimize the workflow; to make the folder/file more structured (e.g., same kind of file in one folder, don't mix different types); 3. easy for knowledge base expansion; 4. write python scripts to filter/diagnose code qualities