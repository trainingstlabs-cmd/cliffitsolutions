"""Default service definitions — used for DB seeding only."""

DEFAULT_SERVICES = {
    "it-staffing": {
        "title": "IT Staffing & Recruiting",
        "color": "blue",
        "tagline": "The Right Talent. Right Now.",
        "description": "Access pre-vetted technology professionals on a contract, contract-to-hire, or direct placement basis. Our deep talent network spans every major tech domain.",
        "details": [
            "Our staffing services cover the full spectrum of technology roles — from junior developers to C-level executives. With a database of over 1,000 pre-screened professionals, we can fill critical positions in days, not months.",
            "Every candidate undergoes rigorous technical assessment, background verification, and culture-fit evaluation before being presented to you. We stand behind our placements with performance guarantees."
        ],
        "features": [
            {"title": "Contract Staffing", "desc": "Flexible short and long-term technology talent to meet project demands and seasonal peaks."},
            {"title": "Contract-to-Hire", "desc": "Evaluate talent on the job before making a permanent hiring decision, reducing risk."},
            {"title": "Direct Placement", "desc": "Full-cycle recruiting for permanent positions, from sourcing through offer negotiation."},
            {"title": "Managed Teams", "desc": "Fully managed, dedicated teams scaled to your project requirements with our oversight."}
        ]
    },
    "digital-transformation": {
        "title": "Digital Transformation",
        "color": "green",
        "tagline": "Modernize. Innovate. Accelerate.",
        "description": "Modernize your technology stack with cloud migration, application modernization, and data-driven strategies that accelerate your digital maturity.",
        "details": [
            "Digital transformation isn't just about technology — it's about reimagining how your business creates value. Our consultants partner with you to assess your current state, define a transformation roadmap, and execute systematically.",
            "From legacy system modernization to greenfield innovation, we bring the technical depth and strategic thinking to make your transformation a success."
        ],
        "features": [
            {"title": "Digital Strategy", "desc": "Comprehensive roadmaps aligned with business objectives and market opportunities."},
            {"title": "Legacy Modernization", "desc": "Re-platform and re-architect aging systems to modern, scalable architectures."},
            {"title": "Process Automation", "desc": "Streamline operations with RPA, workflow automation, and intelligent process mining."},
            {"title": "Change Management", "desc": "Ensure adoption success with training, communication plans, and organizational alignment."}
        ]
    },
    "application-development": {
        "title": "Application Development",
        "color": "purple",
        "tagline": "From Concept to Production.",
        "description": "Custom software solutions built with modern frameworks and agile methodology. From MVPs to enterprise platforms, we bring your vision to production.",
        "details": [
            "Our development teams specialize in full-stack engineering using modern languages and frameworks including React, Angular, Node.js, Python, Java, .NET, and Go. We follow agile methodologies with continuous integration and delivery.",
            "Whether you need a customer-facing mobile app, an internal enterprise tool, or a complex microservices platform, we deliver clean, maintainable code that scales with your business."
        ],
        "features": [
            {"title": "Web Applications", "desc": "Responsive, performant web apps using React, Angular, Vue, and modern backend frameworks."},
            {"title": "Mobile Development", "desc": "Native and cross-platform mobile apps for iOS and Android with seamless UX."},
            {"title": "API & Integration", "desc": "RESTful APIs, GraphQL services, and system integrations that connect your ecosystem."},
            {"title": "DevOps & CI/CD", "desc": "Automated pipelines, infrastructure as code, and continuous delivery practices."}
        ]
    },
    "cloud-infrastructure": {
        "title": "Cloud & Infrastructure",
        "color": "orange",
        "tagline": "Built for Scale. Optimized for Cost.",
        "description": "Design, migrate, and manage cloud environments across AWS, Azure, and GCP. We optimize for performance, security, and cost efficiency.",
        "details": [
            "Our certified cloud architects design and implement infrastructure solutions that balance performance, reliability, and cost. We're partners with all major cloud providers and hold advanced certifications across AWS, Azure, and Google Cloud.",
            "From lift-and-shift migrations to cloud-native re-architecture, we handle the full journey — including ongoing optimization and managed services to keep your environments running at peak efficiency."
        ],
        "features": [
            {"title": "Cloud Migration", "desc": "Seamless migration of workloads with minimal downtime using proven frameworks."},
            {"title": "Architecture Design", "desc": "Scalable, resilient architectures designed for high availability and disaster recovery."},
            {"title": "Cost Optimization", "desc": "Continuous monitoring and right-sizing to reduce cloud spend by 20-40%."},
            {"title": "Managed Services", "desc": "24/7 monitoring, patching, and incident response for your cloud infrastructure."}
        ]
    },
    "cybersecurity": {
        "title": "Cybersecurity Services",
        "color": "red",
        "tagline": "Protect What Matters Most.",
        "description": "Protect your business with threat assessment, SOC operations, compliance consulting, and incident response from seasoned security professionals.",
        "details": [
            "Cyber threats evolve constantly, and your defenses need to stay ahead. Our security practice combines offensive and defensive expertise to protect your organization across every attack surface.",
            "From vulnerability assessments and penetration testing to full SOC-as-a-Service, we provide the expertise and technology to secure your business and maintain regulatory compliance."
        ],
        "features": [
            {"title": "Security Assessment", "desc": "Comprehensive vulnerability scanning, penetration testing, and risk analysis."},
            {"title": "SOC Operations", "desc": "24/7 security operations center with real-time threat detection and response."},
            {"title": "Compliance", "desc": "Expert guidance for SOC 2, HIPAA, PCI-DSS, GDPR, and industry-specific regulations."},
            {"title": "Incident Response", "desc": "Rapid containment, forensic investigation, and recovery from security incidents."}
        ]
    },
    "ai-data-analytics": {
        "title": "AI & Data Analytics",
        "color": "teal",
        "tagline": "Turn Data Into Decisions.",
        "description": "Unlock the power of your data with machine learning, business intelligence, and AI-driven automation that turns insights into competitive advantage.",
        "details": [
            "Data is your most valuable asset — if you can harness it. Our data engineers and AI specialists help you build the pipelines, models, and dashboards that transform raw data into actionable business intelligence.",
            "From predictive analytics to generative AI integration, we bring cutting-edge capabilities to organizations of every size, with a practical focus on ROI and business impact."
        ],
        "features": [
            {"title": "Data Engineering", "desc": "Build robust data pipelines, warehouses, and lakes on modern platforms."},
            {"title": "Machine Learning", "desc": "Custom ML models for prediction, classification, recommendation, and NLP."},
            {"title": "Business Intelligence", "desc": "Interactive dashboards and reporting using Tableau, Power BI, and Looker."},
            {"title": "AI Integration", "desc": "Embed generative AI, chatbots, and intelligent automation into your workflows."}
        ]
    }
}

DEFAULT_SERVICE_ORDER = [
    "it-staffing", "digital-transformation", "application-development",
    "cloud-infrastructure", "cybersecurity", "ai-data-analytics"
]
