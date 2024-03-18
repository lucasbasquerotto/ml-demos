#!/usr/bin/env python
# coding: utf-8

# # Demo

# ## Load Environment Vars



from dotenv import load_dotenv
load_dotenv('../.env')


# ## Data Models



from langchain_core.pydantic_v1 import BaseModel, Field

class Subcategory(BaseModel):
    """A project subcategory."""
    
    id: int = Field(description="The subcategory id.")
    name: str = Field(description="The subcategory name.")

class ReprovationReason(BaseModel):
    """A project reprovation reason."""
    
    id: int = Field(description="The reprovation reason id.")
    name: str = Field(description="The reprovation reason name.")
    description: str = Field(description="The reprovation reason description.")
    other: bool = Field(description="Whether the reprovation reason is an 'other' reason.", default=False)

class ProjectInput(BaseModel):
    """The project data defined by the client (may need changes)."""
    
    subcategory: int = Field(description="The subcategory of the project.")
    title: str = Field(description="The title of the project.")
    description: str = Field(description="The description of the project.")
    abilities: list[str] | None = Field(description="The abilities desired for the project.")
    private: bool = Field(description="Whether the project is private or not.", default=False)

    def format(self):
        abilities_section = ('\n\nHabilidades: ' + ', '.join(self.abilities)) if len(self.abilities or []) else ''
        private_section = '\n\nEste projeto é privado.' if self.private else '\n\nEste projeto é público.'
        return f'{self.title}{private_section}{abilities_section}\n\n{self.description}'
    
class ProjectPrediction(BaseModel):
    """The predicted project data based on the input. Some fields might be left undefined depending on the project being approved or not."""
    
    approve: bool = Field(description="Whether the project should be approved or not.")
    subcategory: int | None = Field(description="The subcategory of the project (when approved).")
    title: str | None = Field(description="The title of the project (when approved).", min_length=25, max_length=75)
    description: str | None = Field(description="The description of the project (when approved).", min_length=50, max_length=2000)
    reprovation_reason: int | None = Field(description="The reason for the project to be reproved (when reproved).")
    reprovation_comment: str | None = Field(description="The comment for the reprovation (when reproved).",)
    
class ProjectInfo(BaseModel):
    """Additional information about the project."""
    
    reasoning: str = Field(description="The reasoning behind the prediction.")
    confidence: float = Field(description="The confidence of the prediction.", ge=0, le=1)
    bot_generated: float = Field(description="How likely is for the project to be bot generated.", ge=0, le=1)
    
    
class ProjectOutput(BaseModel):
    """The predicted project data based on the input, along with additional information."""
    
    prediction: ProjectPrediction = Field(description="The predicted project data based on the input.")
    info: ProjectInfo = Field(description="Additional information about the project.")
    
    
class ProjectApprovation(BaseModel):
    """The project input and prediction for the approvation process."""
    
    input: ProjectInput = Field(description="The project input.")
    prediction: ProjectPrediction = Field(description="The predicted project data based on the input.")


# ## Create Store



from langchain_core.vectorstores import VectorStore
import typing

T = typing.TypeVar('T')

class MyVectorStores:
    def __init__(
            self,
            subcategories: VectorStore,
            reprovation_reasons: VectorStore,
            approved_projects: VectorStore,
            reproved_projects: VectorStore):
        self.subcategories = subcategories
        self.reprovation_reasons = reprovation_reasons
        self.approved_projects = approved_projects
        self.reproved_projects = reproved_projects

class VectorStoreHandler(typing.Generic[T]):
    def __init__(self, store: VectorStore, json_parser: typing.Callable[[str], T]):
        self.store = store
        self.json_parser = json_parser
        
    def get_by_id(self, id: int):
        data = self.store.get(ids=[str(id)])
        metadatas = data['metadatas']
        metadata = metadatas[0] if len(metadatas or []) else None
        json_data = metadata['json'] if metadata else None
        data = self.json_parser(json_data) if json_data else None
        return data
    
    def similarity_search(
            self, 
            query: str, 
            k: int = 5):
        documents = self.store.similarity_search(query, k=k)
        return list(map(lambda d: self.json_parser(d.metadata['json']), documents))
    
    async def asimilarity_search(
            self, 
            query: str, 
            k: int = 5):
        documents = await self.store.asimilarity_search(query, k=k)
        return list(map(lambda d: self.json_parser(d.metadata['json']), documents))
    
    def max_marginal_relevance_search(
            self, 
            query: str, 
            k: int = 5):
        documents = self.store.max_marginal_relevance_search(query, k=k)
        return list(map(lambda d: self.json_parser(d.metadata['json']), documents))
    
    async def amax_marginal_relevance_search(
            self, 
            query: str, 
            k: int = 5):
        documents = await self.store.amax_marginal_relevance_search(query, k=k)
        return list(map(lambda d: self.json_parser(d.metadata['json']), documents))

class MyVectorStoreHandler:
    def __init__(self, stores: MyVectorStores):
        self.subcategories = VectorStoreHandler(store=stores.subcategories, json_parser=Subcategory.parse_raw)
        self.reprovation_reasons = VectorStoreHandler(store=stores.reprovation_reasons, json_parser=ReprovationReason.parse_raw)
        self.approved_projects = VectorStoreHandler(store=stores.approved_projects, json_parser=ProjectApprovation.parse_raw)
        self.reproved_projects = VectorStoreHandler(store=stores.reproved_projects, json_parser=ProjectApprovation.parse_raw)




from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

data_dir = "./data/chroma_db"
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def create_store(collection_name):
    return Chroma(persist_directory=data_dir, collection_name=collection_name, embedding_function=embeddings)

def create_stores():
    stores = MyVectorStores(
        subcategories=create_store("subcategories"),
        reprovation_reasons=create_store("reprovation_reasons"),
        approved_projects=create_store("approved_projects"),
        reproved_projects=create_store("reproved_projects"),
    )
    stores_handler = MyVectorStoreHandler(stores)
    return stores, stores_handler

stores, stores_handler = create_stores()


# ## Examples



def get_subcategories():
    return [
        Subcategory(id=1, name="Design gráfico"),
        Subcategory(id=2, name="Desenvolvimento Web"),
        Subcategory(id=3, name="Redação"),
        Subcategory(id=4, name="Edição de Vídeo"),
        Subcategory(id=5, name="Tradução"),
        Subcategory(id=6, name="Assistente Virtual"),
        Subcategory(id=7, name="Animação"),
        Subcategory(id=8, name="Marketing Digital"),
        Subcategory(id=9, name="Ilustração"),
    ]

def get_reprovation_reasons():
    return [
        ReprovationReason(id=1, name="Outro Motivo", description="", other=True),
        ReprovationReason(id=2, name="Projeto Duplicado", description="Você publicou um projeto muito parecido ou idêntico a esse a pouco tempo"),
        ReprovationReason(id=3, name="Proposta para Trabalhar", description="Se o seu objetivo é encontrar trabalhos, por favor, altere o seu perfil para o de Freelancer"),
        ReprovationReason(id=4, name="Conteúdo Não Permitido", description="Há conteúdo não permitido na descrição do projeto (informações de contato, orçamento, solicitação de testes não remunerados, etc)"),
        ReprovationReason(id=5, name="Projeto Confuso", description="Não está claro o que é pedido no projeto"),
        ReprovationReason(id=6, name="Poucos Detalhes", description="Os freelancers precisam saber detalhes para que possam enviar as suas propostas. Seja o mais específico possível"),
        ReprovationReason(id=7, name="Pagamento Comissionado", description="Projetos com pagamentos parciais ou totais via comissão não são permitidos"),
        ReprovationReason(id=8, name="Requer trabalho não pago", description="Todo trabalho deve ser pago"),
        ReprovationReason(id=9, name="Troca de trabalho", description="Permutas não são permitidas"),
        ReprovationReason(id=10, name="Vaga de emprego", description="Nosso site é somente para trabalhos temporários. Não podemos te ajudar a encontrar profissionais para ocupar cargos na sua empresa"),
        ReprovationReason(id=11, name="Trabalhos acadêmicos", description="O seu trabalho não pode ser feito por outra pessoa. Valorize a sua educação"),
        ReprovationReason(id=12, name="Ilegal", description="Está solicitando algo que é ilegal ou que será utilizado para fins não permitidos"),
        ReprovationReason(id=13, name="Sem demanda", description="Está recrutando profissionais para parceria ou para demandas futuras"),
        ReprovationReason(id=14, name="Não Permitido", description="Esse tipo de trabalho não é permitido"),
    ]

def get_projects_approvation_full(idx):
    project_id = idx + 1
    
    if idx % 10 == 0:
        input = ProjectInput(
            subcategory=1,
            title=f"PRECISO DE DESIGNER GRFICO - #{project_id}",
            description=f"Preciso de desgner grafico para criação de logotipo\nMeu telefone é 98765-4321",
            abilities=["Criação de logotipo", "Ilustração"],
            private=False,
        )
        prediction = ProjectPrediction(
            approve=True,
            subcategory=1,
            title=f"Designer gráfico para criação de Logotipo - #{project_id}",
            description=f"Preciso de designer gráfico para criação de logotipo.",
        )
        info = ProjectInfo(
            reasoning="Alteração do título para ficar mais conciso e ajustes em sua capitalização. Correções ortográficas na descrição. Remoção de telefone de contato.",
            confidence=0.8,
            bot_generated=0.4,
        )
    elif idx % 10 == 1:
        input = ProjectInput(
            subcategory=0,
            title=f"ESCREVER ARTIGOS PARA BLOG - #{project_id}",
            description=f"Preciso de redaor para criação de conteúdo para meu blog https://meublog.com",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=True,
            subcategory=3,
            title=f"Escrever artigos para blog - #{project_id}",
            description=f"Preciso de redator para criação de conteúdo para meu blog https://meublog.com",
        )
        info = ProjectInfo(
            reasoning="Ajustes na capitalização do título. Correção de erro ortográfico na descrição.",
            confidence=0.7,
            bot_generated=0.3,
        )
    elif idx % 10 == 2:
        input = ProjectInput(
            subcategory=0,
            title=f"TRADUÇÃO DE TEXTO - #{project_id}",
            description=f"Preciso de tradutor para traduzir texto de inglês para português. Primeiramente será feito um teste não pago para depois ser decidido o freelancer que fará o projeto.",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=False,
            reprovation_reason=8,            
        )
        info = ProjectInfo(
            reasoning="Testes não pagos não são permitidos.",
            confidence=0.8,
            bot_generated=0.3,
        )
    elif idx % 10 == 3:
        input = ProjectInput(
            subcategory=8,
            title=f"Assistente virtual para tarefa pontual - #{project_id}",
            description=f"Preciso de assistente virtual para realizar tarefas administrativas com duração de 2 dias. Deverá saber utilizar planilhas do Excel e ter conexão com a internet. Será feito home office.",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=True,
            subcategory=6,
            title=f"Assistente virtual para tarefa pontual - #{project_id}",
            description=f"Preciso de assistente virtual para realizar tarefas administrativas com duração de 2 dias. Deverá saber utilizar planilhas do Excel e ter conexão com a internet. Será feito home office.",
        )
        info = ProjectInfo(
            reasoning="Nenhuma alteração necessária.",
            confidence=0.9,
            bot_generated=0.2,
        )
    elif idx % 10 == 4:
        input = ProjectInput(
            subcategory=0,
            title=f"Crawler de Website - #{project_id}",
            description=f"Preciso de alguém que faça um crawler para coletar informações de um website. Deverá acessar a API e burlar o CAPTCHA, se necessário.",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=False,
            reprovation_reason=12,
            reprovation_comment="Solicitação de algo não permitido (burlar CAPTCHA).",
        )
        info = ProjectInfo(
            reasoning="Solicitação de algo não permitido (burlar CAPTCHA).",
            confidence=0.8,
            bot_generated=0.3,
        )
    elif idx % 10 == 5:
        input = ProjectInput(
            subcategory=0,
            title=f"Desenvolvimento de Website - #{project_id} - Freelancer Jorge",
            description=f"Criar um website para mim. Deverá ser responsivo e ter um design limpo. Projeto para ser feito pelo freelancer Jorge conforme combinado. Contactar pelo telefone 98765-4321.",
            private=True,
        )
        prediction = ProjectPrediction(
            approve=True,
            subcategory=2,
            title=f"Desenvolvimento de Website - #{project_id} - Freelancer Jorge",
            description=f"Criar um website para mim. Deverá ser responsivo e ter um design limpo. Projeto para ser feito pelo freelancer Jorge conforme combinado. Contactar pelo telefone 98765-4321.",
        )
        info = ProjectInfo(
            reasoning="Alteração da subcategoria. Projetos privados aceitam propostas de freelancers específicos e com informação de contato, então não houve alteração na descrição.",
            confidence=0.9,
            bot_generated=0.2,
        )
    elif idx % 10 == 6:
        input = ProjectInput(
            subcategory=0,
            title=f"Desenvolvimento de Website - #{project_id} - Freelancer Jorge",
            description=f"Criar um website para mim. Deverá ser responsivo e ter um design limpo. Projeto para ser feito pelo freelancer Jorge conforme combinado. Contactar pelo telefone 98765-4321.",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=False,
            reprovation_reason=1,
            reprovation_comment="Para fazer um projeto com um freelancer específico, é necessário que o projeto seja privado (é possível definir no formulário de publicação do projeto para que ele seja privado).",
        )
        info = ProjectInfo(
            reasoning="Para fazer um projeto com um freelancer específico, é necessário que o projeto seja privado (é possível definir no formulário de publicação do projeto para que ele seja privado).",
            confidence=0.9,
            bot_generated=0.2,
        )
    elif idx % 10 == 7:
        input = ProjectInput(
            subcategory=2,
            title=f"Freelancer para criação de artes - #{project_id}",
            description=f"Preciso de um freelancer para criar artes para mim conforme a demanda.",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=False,
            reprovation_reason=13,
        )
        info = ProjectInfo(
            reasoning="Os projetos devem ter um escopo bem definido para que os freelancers possam enviar propostas. O projeto foi reprovado porque o que foi solicitado é muito vago e não é referente a um trabalho específico a ser feito.",
            confidence=0.9,
            bot_generated=0.4,
        )
    elif idx % 10 == 8:
        input = ProjectInput(
            subcategory=0,
            title=f"DEPOIMENTO PARA PRODUTO DE SKINCARE - #{project_id}",
            description=f"Procuro alguém talentoso e criativo para criar um vídeo promocional de alta qualidade, com duração de 1 minuto, para promover nosso novo produto de skincare. Este vídeo será fundamental para apresentar e destacar os benefícios únicos do nosso produto, cativando nosso público-alvo e gerando interesse em nossa marca.",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=True,
            subcategory=8,
            title=f"Depoimento para produto de skincare - #{project_id}",
            description=f"Procuro alguém talentoso e criativo para criar um vídeo promocional de alta qualidade, com duração de 1 minuto, para promover nosso novo produto de skincare. Este vídeo será fundamental para apresentar e destacar os benefícios únicos do nosso produto, cativando nosso público-alvo e gerando interesse em nossa marca.",
        )
        info = ProjectInfo(
            reasoning="Alterações na capitalização do título.",
            confidence=0.9,
            bot_generated=0.4,
        )
    elif idx % 10 == 9:
        input = ProjectInput(
            subcategory=1,
            title=f"DEPOIMENTO PARA PRODUTO DE SKINCARE - #{project_id}",
            description=f"PROCURO ALGUÉM TALENTOSO E CRIATIVO PARA CRIAR UM VÍDEO PROMOCINAL DE ALTA QUALIDADE, COM DURAÇÃO DE 1 MINUTO, PARA PROMOVER NOSO NOVO PRODUTO DE SKINCARE. ESTE VÍDEO SERÁ FUNDAMENTAL PARA APRESENTAR E DESTACAR OS BENEFÍCIOS ÚNICOS DO NOSSO PRODUTO, CATIVANDO NOSSO PÚBLICO-ALVO E GERANDO INTERESSE EM NOSSA MARCA.",
            private=False,
        )
        prediction = ProjectPrediction(
            approve=True,
            subcategory=8,
            title=f"Depoimento para produto de skincare - #{project_id}",
            description=f"Procuro alguém talentoso e criativo para criar um vídeo promocional de alta qualidade, com duração de 1 minuto, para promover nosso novo produto de skincare. Este vídeo será fundamental para apresentar e destacar os benefícios únicos do nosso produto, cativando nosso público-alvo e gerando interesse em nossa marca.",
        )
        info = ProjectInfo(
            reasoning="Alterações na capitalização do título e da descrição e correções na descrição.",
            confidence=0.9,
            bot_generated=0.4,
        )

    output = ProjectOutput(prediction=prediction, info=info)
    return project_id, input, output

def get_full_examples(amount: int):
    return [get_projects_approvation_full(i) for i in range(amount)]


# ## Load Examples



# Examples of a pretend task of creating antonyms.
examples = get_full_examples(100)




examples[:2]




[
    stores.subcategories.add_texts(
        ids=[str(item.id)], 
        texts=[item.name], 
        metadatas=[dict(id=item.id, json=item.json(ensure_ascii=False))]
    ) for item in get_subcategories()
]
[
    stores.reprovation_reasons.add_texts(
        ids=[str(item.id)], 
        texts=[item.name], 
        metadatas=[dict(id=item.id, json=item.json(ensure_ascii=False))]
    ) for item in get_reprovation_reasons()
]
[
    stores.approved_projects.add_texts(
        ids=[str(project_id)], 
        texts=[data.input.format()], 
        metadatas=[dict(id=project_id, json=data.json(ensure_ascii=False))]
    ) for project_id, data in [
        (project_id, ProjectApprovation(input=input, prediction=output.prediction)) 
        for project_id, input, output in examples
        if output.prediction.approve
    ]
]
[
    stores.reproved_projects.add_texts(
        ids=[str(project_id)], 
        texts=[data.input.format()], 
        metadatas=[dict(id=project_id, json=data.json(ensure_ascii=False))]
    ) for project_id, data in [
        (project_id, ProjectApprovation(input=input, prediction=output.prediction)) 
        for project_id, input, output in examples
        if not output.prediction.approve
    ]
]

stores, stores_handler = create_stores()


# ## Print examples loaded from the stores



from pprint import pprint




pprint(stores_handler.subcategories.similarity_search("design", k=3))




pprint(stores_handler.reprovation_reasons.similarity_search("duplicado", k=3))




pprint(stores_handler.approved_projects.similarity_search("desenho", k=3))




pprint(stores_handler.reproved_projects.similarity_search("website", k=3))




stores_handler.subcategories.similarity_search("design")[0]




stores_handler.reprovation_reasons.similarity_search("duplicado")[0]




stores_handler.approved_projects.similarity_search("desenho")[0]




stores_handler.reproved_projects.similarity_search("website")[0]




stores_handler.subcategories.get_by_id(1)




stores_handler.reprovation_reasons.get_by_id(2)




stores_handler.approved_projects.get_by_id(4)




stores_handler.reproved_projects.get_by_id(3)


# ## Create the ids mapper prompt



async def subcategories_prompt(input_query: str, k=50):    
    filtered = await stores_handler.subcategories.asimilarity_search(input_query, k=min(k, len(stores.subcategories.get(limit=k)['ids'])))
    filtered.insert(0, Subcategory(id=0, name="Outra categoria"))
    filtered = sorted(filtered, key=lambda x: x.id)
    result = 'Subcategories ([ID]: [NAME]):\n\n' + '\n'.join([f"{item.id}: {item.name}" for item in filtered])
    return result




async def reprovation_reasons_prompt(input_query: str, k=50):
    filtered = await stores_handler.reprovation_reasons.asimilarity_search(input_query, k=min(k, len(stores.reprovation_reasons.get(limit=k)['ids'])))
    
    if not any(item.other for item in filtered):
        filtered.insert(0, ReprovationReason(id=1, name="Outro Motivo", description=""))

    filtered = sorted(filtered, key=lambda x: x.id)

    result = 'Reprovation reasons ([ID]: [NAME] (DESCRIPTION)):\n\n' + '\n'.join(
        [f"{item.id}: {item.name} ({item.description or '-'})" for item in filtered])
    
    return result


# ## Create the examples prompt



async def examples_prompt(input_query: str, k=5):
    approved = await stores_handler.approved_projects.asimilarity_search(input_query, k=k)
    reproved = await stores_handler.reproved_projects.asimilarity_search(input_query, k=k)

    result = 'Partial examples of inputs and predictions (used for the complete output):\n\n' + '\n\n'.join([
        f"Input: {example.input.json(ensure_ascii=False)}\nPrediction: {example.prediction.json(ensure_ascii=False)}" 
        for example in (approved + reproved)
    ])

    return result




def full_example_item_prompt(input: str, output: str):
    return f"Input: {input}\nOutput: {output}" 

def full_examples_prompt(full_examples: list[tuple[ProjectInput, ProjectOutput]]):
    result = 'Examples of inputs and the corresponding full output:\n\n' + '\n\n'.join([
        f"{item_prompt}" for item_prompt in [
            full_example_item_prompt(input=input.json(ensure_ascii=False), output=output.json(ensure_ascii=False))
            for input, output in full_examples
        ]
    ])

    return result


# ## Full Prompt

from langchain_core.output_parsers.base import BaseOutputParser, T

async def system_prompt(input: ProjectInput, parser: BaseOutputParser[T]):
    input_query = input.format()
    subcategories = await subcategories_prompt(input_query, k=50)
    reprovation_reasons = await reprovation_reasons_prompt(input_query, k=50)
    examples = await examples_prompt(input_query, k=20)
    full_examples = full_examples_prompt([(input, output) for _, input, output in get_full_examples(10)])
    format_instructions = parser.get_format_instructions()
    
    result = f"""
        Return the expected output for the project approvation process based on the input.

        The output is composed by a prediction according to the input and additional information about the project.

        This additional information is a meta information given by you according to your reasoning about the project and the prediction itself.

        Projects should be reproved if they ask the freelancer to do something that is specified in the reprovation reasons.

        One peculiar case is for contact information. They should be removed in public projects, but should be allowed in private projects.

        A project asking a specific freelancer to do the job must be private, otherwise it should be reproved.
        
        The language of the prediction must be the same as the input language. The default language is Brazilian Portuguese (pt-BR).

        The prediction should change the minimum possible from the input, but it should be improved in terms of grammar and punctuation, if needed.

        You MUST NOT change the meaning of the description. NO MATTER WHAT. If needed, you can define to be reproved if something is really wrong.

        Some data in the predictions must be defined as the id based on the following mappings:

        {subcategories}

        {reprovation_reasons}

        {examples}

        {format_instructions}

        The result that you return must include both the prediction (as defined in the partial examples above) and the additional information (based on your reasoning) as shown below.

        {full_examples}
    """

    result = '\n'.join([line.strip() for line in result.split('\n')])

    return result.strip()

def user_prompt(input: ProjectInput):
    formatted_input = full_example_item_prompt(input=input.json(ensure_ascii=False), output='')
    return formatted_input

async def full_prompt(input: ProjectInput, parser: BaseOutputParser[T]):
    system_prompt_str = await system_prompt(input, parser)
    user_prompt_str = user_prompt(input)
    
    result = f"""
        {system_prompt_str}

        {user_prompt_str}
    """

    result = '\n'.join([line.strip() for line in result.split('\n')])

    return result.strip()

# ## Create the chain

from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def create_chain_parts(chat: bool):
    parser = PydanticOutputParser(pydantic_object=ProjectOutput)

    async def full_prompt_with_parser(input: ProjectInput):
        return await full_prompt(input=input, parser=parser)

    async def system_prompt_with_parser(input: ProjectInput):
        return await system_prompt(input=input, parser=parser)

    if chat:
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template('{system}'),
            HumanMessagePromptTemplate.from_template('{human}'),
        ])
        prompt = dict(
            system=RunnableLambda(system_prompt_with_parser),
            human=RunnableLambda(user_prompt),
        ) | chat_template
        llm = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')
    else:
        prompt = RunnableLambda(full_prompt_with_parser)
        llm = OpenAI(temperature=0)

    return prompt, llm, parser

prompt, llm, parser = create_chain_parts(chat=True)

chain = prompt | llm | parser

# ## Calculate the similarities

from langchain.utils.math import cosine_similarity
import numpy as np

def get_similarity(str1: str, str2: str):
    embed_1 = embeddings.embed_query(str1 or '')
    embed_2 = embeddings.embed_query(str2 or '')
    return cosine_similarity([embed_1], [embed_2])[0][0]

def get_input_similarities(prediction: ProjectPrediction, input: ProjectInput):
    if prediction.approve:
        pred_input = ProjectInput(
            subcategory=prediction.subcategory,
            title=prediction.title,
            description=prediction.description,
            private=input.private)
        
        input_to_compare = ProjectInput(
            subcategory=input.subcategory,
            title=input.title,
            description=input.description,
            private=input.private)
        
        subcategory_1 = stores_handler.subcategories.get_by_id(pred_input.subcategory)
        subcategory_2 = stores_handler.subcategories.get_by_id(input_to_compare.subcategory)
        subcategory_name_1 = subcategory_1.name if subcategory_1 else ''
        subcategory_name_2 = subcategory_2.name if subcategory_2 else ''

        subcategory_similarity = (
            1 
            if pred_input.subcategory == input_to_compare.subcategory 
            else (0.5 * get_similarity(subcategory_name_1, subcategory_name_2)))
        
        title_similarity = get_similarity(pred_input.title, input_to_compare.title)
        description_similarity = get_similarity(pred_input.description, input_to_compare.description)
        similarity = get_similarity(pred_input.format(), input_to_compare.format())

        return dict(
            similarity=similarity,
            subcategory_similarity=subcategory_similarity,
            title_similarity=title_similarity,
            description_similarity=description_similarity,
        )
    else:
        return dict(similarity=1)


def get_output_similarities(prediction: ProjectPrediction, expected: ProjectPrediction):
    if expected.approve and prediction.approve:
        subcategory_1 = stores_handler.subcategories.get_by_id(prediction.subcategory)
        subcategory_2 = stores_handler.subcategories.get_by_id(expected.subcategory)
        subcategory_name_1 = subcategory_1.name if subcategory_1 else ''
        subcategory_name_2 = subcategory_2.name if subcategory_2 else ''

        subcategory_similarity = (
            1 
            if prediction.subcategory == expected.subcategory 
            else (0.5 * get_similarity(subcategory_name_1, subcategory_name_2)))
        title_similarity = get_similarity(prediction.title, expected.title)
        description_similarity = get_similarity(prediction.description, expected.description)
        similarity = np.mean([subcategory_similarity, title_similarity, description_similarity])

        return dict(
            similarity=similarity,
            subcategory_similarity=subcategory_similarity,
            title_similarity=title_similarity,
            description_similarity=description_similarity,
        )
    elif not expected.approve and not prediction.approve:
        reprovation_reason_1 = stores_handler.reprovation_reasons.get_by_id(prediction.reprovation_reason)
        reprovation_reason_2 = stores_handler.reprovation_reasons.get_by_id(expected.reprovation_reason)
        reprovation_reason_name_1 = reprovation_reason_1.name if reprovation_reason_1 else ''
        reprovation_reason_name_2 = reprovation_reason_2.name if reprovation_reason_2 else ''

        reprovation_reason_similarity = (
            1 
            if prediction.reprovation_reason == expected.reprovation_reason 
            else (0.5 * get_similarity(reprovation_reason_name_1, reprovation_reason_name_2)))
        reprovation_comment_similarity = get_similarity(prediction.reprovation_comment, expected.reprovation_comment)
        similarity = (9 * reprovation_reason_similarity + reprovation_comment_similarity) / 10

        return dict(
            similarity=similarity,
            reprovation_reason_similarity=reprovation_reason_similarity,
            reprovation_comment_similarity=reprovation_comment_similarity,
        )
    else:
        return dict(similarity=0)

# ## Tests

def test_similarity(str1: str, str2: str):
    similarity = get_similarity(str1, str2)
    print(f'Similarity between "{str1}" and "{str2}": {similarity:.4f}')

async def invoke_and_show_similarities(input: ProjectInput, output_expected: ProjectOutput):
    print('Input:')
    print(input)

    print()
    print('Output Expected:')
    print(output_expected)

    output_predicted = await chain.ainvoke(input)

    print()
    print('Output Predicted:')
    print(output_predicted)

    input_similarities = get_input_similarities(
        prediction=output_predicted.prediction, 
        input=input)

    print()
    print('Input Similarities:')
    print(input_similarities)

    similarities = get_output_similarities(
        prediction=output_predicted.prediction, 
        expected=output_expected.prediction)

    print()
    print('Output Similarities:')
    print(similarities)
    
    print()

async def fn_main():
    print('-' * 50)
    print('Examples:')
    print('-' * 50)

    [await invoke_and_show_similarities(input=input, output_expected=output_expected) for _, input, output_expected in examples[:5]]

    print('-' * 50)
    print('Correct Example:')
    print('-' * 50)

    input = ProjectInput(
        subcategory=0, 
        title="CRIÇÃO DE CARTÃO DE VISITAS", 
        description="Presciso de um proficional criativo para a criação de um cartão de visitas para a minha empresa de consultoria.",
        private=False,
    )

    output_expected = ProjectOutput(
        prediction=ProjectPrediction(
            approve=True,
            subcategory=1,
            title="Criação de cartão de visitas",
            description="Preciso de um profissional criativo para a criação de um cartão de visitas para a minha empresa de consultoria.",
        ),
        info=ProjectInfo(
            reasoning="Correção de erro ortográfico no título e ajustes em sua capitalização. Correções ortográficas na descrição.",
            confidence=0.8,
            bot_generated=0.4,
        )
    )

    await invoke_and_show_similarities(input=input, output_expected=output_expected)

    print('-' * 50)
    print('Incorrect Example:')
    print('-' * 50)

    prediction = examples[0][2].prediction
    input = examples[3][1]

    print('Input:')
    print(input)

    print()
    print('Output Predicted:')
    print(prediction)

    input_similarities = get_input_similarities(
        prediction=prediction,
        input=input)

    print()
    print('Input Similarities:')
    print(input_similarities)

    prediction = examples[0][2].prediction
    expected = examples[3][2].prediction

    print()
    print('Output Expected:')
    print(expected)

    print()
    print('Output Predicted:')
    print(prediction)

    similarities = get_output_similarities(
        prediction=prediction, 
        expected=expected)

    print()
    print('Output Similarities:')
    print(similarities)

    print()

import asyncio
asyncio.run(fn_main())
