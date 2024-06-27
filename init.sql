-- Table: public.user

-- DROP TABLE IF EXISTS public."user";

CREATE TABLE IF NOT EXISTS public."user"
(
    type_user character varying COLLATE pg_catalog."default",
    email character varying COLLATE pg_catalog."default" NOT NULL,
    password_hash character varying COLLATE pg_catalog."default",
    CONSTRAINT user_pkey PRIMARY KEY (email)
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."user"
    OWNER to postgres;

-- Table: public.invoice_input

-- DROP TABLE IF EXISTS public.invoice_input;

CREATE TABLE IF NOT EXISTS public.invoice_input
(
    invoice_id character varying COLLATE pg_catalog."default" NOT NULL,
    pdf_file_name character varying COLLATE pg_catalog."default",
    pdf_file_input bytea,
    email character varying COLLATE pg_catalog."default",
    json_file_input json,
    creation_date date,
    CONSTRAINT invoice_input_pkey PRIMARY KEY (invoice_id),
    CONSTRAINT email FOREIGN KEY (email)
        REFERENCES public."user" (email) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.invoice_input
    OWNER to postgres;
