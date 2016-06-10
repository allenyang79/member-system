# -*- coding: utf-8 -*-

import inspect
import graphene
#import models
#from models import db_session
#from models import Person as PersonModel
#from models import Department as DepartmentModel
#from models import Employee as EmployeeModel


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

    def create(self):
        print "==create=="
        print dir(self)

class Query(graphene.ObjectType):
    gender = graphene.Field(Gender)
    person = graphene.Field(Person)
    find_person = graphene.Field(Person)

    def resolve_find_person(self, args, info):
        #raise InvalidError('Hello World Error')
        return Person(name='Peter', address='this is address')


class CreatePerson(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    result = graphene.Field('Person')

    class Input:
        social_id = graphene.String()
        name = graphene.String()
        phone = graphene.String()
        address = graphene.String()
        email = graphene.String()
        gender = Gender()

    @classmethod
    def mutate(cls, instance, args, info):
        print "==mutate=="
        print instance
        print args
        print info
        kw = {}
        for field in (
                'social_id',
                'name',
                'phone',
                'address',
                'email',
                'gender',
            ):
            if field in args:
                kw[field] = args.get(field)

        if kw:
            person = Person(**kw)
            person.create()
            ok = True
            return CreatePerson(
                ok=ok,
                result=person
            )


class MyMutations(graphene.ObjectType):
    create_person = graphene.Field(CreatePerson)


class InvalidErrorMiddleware(object):
    @classmethod
    def resolve(cls, next, root, args, context, info):
        try:
            return next(root, args, context, info)
        except InvalidError as e:
            raise e
            # print '[error]', e.message
            # return None
            # return

schema = graphene.Schema(
    query=Query,
    mutation=MyMutations,
    middlewares=[InvalidErrorMiddleware]
)
