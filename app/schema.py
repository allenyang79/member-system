# -*- coding: utf-8 -*-

import inspect

import graphene
import models
from models import db_session
from models import Person as PersonModel
#from models import Department as DepartmentModel
#from models import Employee as EmployeeModel

'''
class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')
    ping = graphene.String(description='Ping someone',
                           to=graphene.String())

    def resolve_hello(self, args, info):
        return 'World'

    def resolve_ping(self, args, info):
        return 'Pinging {}'.format(args.get('to'))

schema = graphene.Schema(query=Query)
'''

'''
class IPerson(graphene.Interface):
    id = graphene.ID()
    name = graphene.String()



class Person(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()

    @classmethod
    def create(cls, row):
        """create a person from person_model.
        """
        #a = inspect.getargspec(eat_dog)
        #print inspect.getargspec(Person.__init__)
        #return Person(
        #    id = row.id,
        #    name = row.name,
        #)
        #print dict(row)
        return Person(**models.to_dict(row))
'''

class InvalidError(Exception):
    def __init__(self, message, code=0):
        super(InvalidError, self).__init__(message)
        self.code = 0


class Gender(graphene.Enum):
    male = 'male'
    female = 'female'
    unknow = 'unknow'


class Person(graphene.ObjectType):
    _id = graphene.ID()
    social_id = graphene.String()
    name = graphene.String()
    phone = graphene.String()
    address = graphene.String()
    email = graphene.String()
    gender = Gender()

    birthday = graphene.String()
    register_day = graphene.String()
    unregister_day = graphene.String()
    baptize_day = graphene.String()
    baptize_priest = graphene.String()

    education = graphene.String()
    job = graphene.String()

    # groups =
    #events = graphene.List()
    note = graphene.String()

    modified_at = graphene.String()
    created_at = graphene.String()


class Query(graphene.ObjectType):
    gender = graphene.Field(Gender)
    person = graphene.Field(Person)
    find_person = graphene.Field(Person)

    def resolve_find_person(self, args, info):
        raise InvalidError('Hello World Error')
        return Person(name='Peter', address='this is address')


class BaseMutation(graphene.Mutation):
    # response interface
    ok = graphene.Boolean()
    message = graphene.String()


class CreatePerson(BaseMutation):
    result = graphene.Field('Person')

    class Input:
        name = graphene.String()
        gender = Gender()

    @classmethod
    def mutate(cls, instance, args, info):
        try:
            kw = {}
            for field in ('name', 'gender', 'phone'):
                if field == 'gender' and args.get(field) == 'unknow':
                    return BaseMutation(ok=False, message='unknow gender')

                for field in args:
                    kw[field] = args.get(field)

            if kw:
                person = Person(**kw)
                ok = True
                return CreatePerson(
                    ok=ok,
                    result=person
                )
        except Exception as e:
            return BaseMutation(ok=False, message=str(e))


class MyMutations(graphene.ObjectType):
    create_person = graphene.Field(CreatePerson)

class InvalidErrorMiddleware(object):
    @classmethod
    def resolve(cls, next, root, args, context, info):
        try:
            return next(root, args, context, info)
        except InvalidError as e:
            raise e
            #print '[error]', e.message
            #return None
            #return


schema = graphene.Schema(
    query=Query,
    mutation=MyMutations,
    middlewares=[InvalidErrorMiddleware]
)

