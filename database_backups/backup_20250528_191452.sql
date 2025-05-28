--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.supplier_product DROP CONSTRAINT IF EXISTS supplier_product_supplier_id_fkey;
ALTER TABLE IF EXISTS ONLY public.quotation_item DROP CONSTRAINT IF EXISTS quotation_item_supplier_id_fkey;
ALTER TABLE IF EXISTS ONLY public.quotation_item DROP CONSTRAINT IF EXISTS quotation_item_quotation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.quotation_item DROP CONSTRAINT IF EXISTS quotation_item_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.quotation DROP CONSTRAINT IF EXISTS quotation_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.product_update_request DROP CONSTRAINT IF EXISTS product_update_request_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.product_update_request DROP CONSTRAINT IF EXISTS product_update_request_price_list_id_fkey;
ALTER TABLE IF EXISTS ONLY public.price_list DROP CONSTRAINT IF EXISTS price_list_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.price_list_item DROP CONSTRAINT IF EXISTS price_list_item_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.price_list_item DROP CONSTRAINT IF EXISTS price_list_item_price_list_id_fkey;
ALTER TABLE IF EXISTS ONLY public.price_list DROP CONSTRAINT IF EXISTS price_list_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.order_item DROP CONSTRAINT IF EXISTS order_item_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.order_item DROP CONSTRAINT IF EXISTS order_item_price_list_id_fkey;
ALTER TABLE IF EXISTS ONLY public.order_item DROP CONSTRAINT IF EXISTS order_item_order_id_fkey;
ALTER TABLE IF EXISTS ONLY public."order" DROP CONSTRAINT IF EXISTS order_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.lead DROP CONSTRAINT IF EXISTS lead_converted_to_quotation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_item DROP CONSTRAINT IF EXISTS invoice_item_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_item DROP CONSTRAINT IF EXISTS invoice_item_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice DROP CONSTRAINT IF EXISTS invoice_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_addendum_lines DROP CONSTRAINT IF EXISTS invoice_addendum_lines_addendum_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_addenda DROP CONSTRAINT IF EXISTS invoice_addenda_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.import_log DROP CONSTRAINT IF EXISTS import_log_imported_by_fkey;
ALTER TABLE IF EXISTS ONLY public.file_upload DROP CONSTRAINT IF EXISTS file_upload_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_contact DROP CONSTRAINT IF EXISTS customer_contact_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer DROP CONSTRAINT IF EXISTS customer_category_id_fkey;
DROP INDEX IF EXISTS public.product_sku_unique_idx;
ALTER TABLE IF EXISTS ONLY public."user" DROP CONSTRAINT IF EXISTS user_username_key;
ALTER TABLE IF EXISTS ONLY public."user" DROP CONSTRAINT IF EXISTS user_pkey;
ALTER TABLE IF EXISTS ONLY public.supplier_product DROP CONSTRAINT IF EXISTS supplier_product_pkey;
ALTER TABLE IF EXISTS ONLY public.supplier DROP CONSTRAINT IF EXISTS supplier_pkey;
ALTER TABLE IF EXISTS ONLY public.supplier DROP CONSTRAINT IF EXISTS supplier_name_key;
ALTER TABLE IF EXISTS ONLY public.quotation DROP CONSTRAINT IF EXISTS quotation_quotation_number_key;
ALTER TABLE IF EXISTS ONLY public.quotation DROP CONSTRAINT IF EXISTS quotation_pkey;
ALTER TABLE IF EXISTS ONLY public.quotation_item DROP CONSTRAINT IF EXISTS quotation_item_pkey;
ALTER TABLE IF EXISTS ONLY public.product_update_request DROP CONSTRAINT IF EXISTS product_update_request_pkey;
ALTER TABLE IF EXISTS ONLY public.product DROP CONSTRAINT IF EXISTS product_pkey;
ALTER TABLE IF EXISTS ONLY public.price_list DROP CONSTRAINT IF EXISTS price_list_pkey;
ALTER TABLE IF EXISTS ONLY public.price_list_item DROP CONSTRAINT IF EXISTS price_list_item_pkey;
ALTER TABLE IF EXISTS ONLY public."order" DROP CONSTRAINT IF EXISTS order_pkey;
ALTER TABLE IF EXISTS ONLY public."order" DROP CONSTRAINT IF EXISTS order_order_number_key;
ALTER TABLE IF EXISTS ONLY public.order_item DROP CONSTRAINT IF EXISTS order_item_pkey;
ALTER TABLE IF EXISTS ONLY public.lead DROP CONSTRAINT IF EXISTS lead_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice DROP CONSTRAINT IF EXISTS invoice_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_item DROP CONSTRAINT IF EXISTS invoice_item_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice DROP CONSTRAINT IF EXISTS invoice_invoice_number_key;
ALTER TABLE IF EXISTS ONLY public.invoice_addendum_lines DROP CONSTRAINT IF EXISTS invoice_addendum_lines_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_addenda DROP CONSTRAINT IF EXISTS invoice_addenda_pkey;
ALTER TABLE IF EXISTS ONLY public.import_log DROP CONSTRAINT IF EXISTS import_log_pkey;
ALTER TABLE IF EXISTS ONLY public.file_upload DROP CONSTRAINT IF EXISTS file_upload_pkey;
ALTER TABLE IF EXISTS ONLY public.customer DROP CONSTRAINT IF EXISTS customer_pkey;
ALTER TABLE IF EXISTS ONLY public.customer_contact DROP CONSTRAINT IF EXISTS customer_contact_pkey;
ALTER TABLE IF EXISTS ONLY public.customer_category DROP CONSTRAINT IF EXISTS customer_category_pkey;
ALTER TABLE IF EXISTS ONLY public.company_settings DROP CONSTRAINT IF EXISTS company_settings_pkey;
ALTER TABLE IF EXISTS public."user" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.supplier_product ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.supplier ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quotation_item ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quotation ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.product_update_request ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.product ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.price_list_item ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.price_list ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.order_item ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."order" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.lead ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoice_item ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoice ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.import_log ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.file_upload ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer_contact ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer_category ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.company_settings ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.user_id_seq;
DROP TABLE IF EXISTS public."user";
DROP SEQUENCE IF EXISTS public.supplier_product_id_seq;
DROP TABLE IF EXISTS public.supplier_product;
DROP SEQUENCE IF EXISTS public.supplier_id_seq;
DROP TABLE IF EXISTS public.supplier;
DROP SEQUENCE IF EXISTS public.quotation_item_id_seq;
DROP TABLE IF EXISTS public.quotation_item;
DROP SEQUENCE IF EXISTS public.quotation_id_seq;
DROP TABLE IF EXISTS public.quotation;
DROP SEQUENCE IF EXISTS public.product_update_request_id_seq;
DROP TABLE IF EXISTS public.product_update_request;
DROP SEQUENCE IF EXISTS public.product_id_seq;
DROP TABLE IF EXISTS public.product;
DROP SEQUENCE IF EXISTS public.price_list_item_id_seq;
DROP TABLE IF EXISTS public.price_list_item;
DROP SEQUENCE IF EXISTS public.price_list_id_seq;
DROP TABLE IF EXISTS public.price_list;
DROP SEQUENCE IF EXISTS public.order_item_id_seq;
DROP TABLE IF EXISTS public.order_item;
DROP SEQUENCE IF EXISTS public.order_id_seq;
DROP TABLE IF EXISTS public."order";
DROP SEQUENCE IF EXISTS public.lead_id_seq;
DROP TABLE IF EXISTS public.lead;
DROP SEQUENCE IF EXISTS public.invoice_item_id_seq;
DROP TABLE IF EXISTS public.invoice_item;
DROP SEQUENCE IF EXISTS public.invoice_id_seq;
DROP TABLE IF EXISTS public.invoice_addendum_lines;
DROP TABLE IF EXISTS public.invoice_addenda;
DROP TABLE IF EXISTS public.invoice;
DROP SEQUENCE IF EXISTS public.import_log_id_seq;
DROP TABLE IF EXISTS public.import_log;
DROP SEQUENCE IF EXISTS public.file_upload_id_seq;
DROP TABLE IF EXISTS public.file_upload;
DROP SEQUENCE IF EXISTS public.customer_id_seq;
DROP SEQUENCE IF EXISTS public.customer_contact_id_seq;
DROP TABLE IF EXISTS public.customer_contact;
DROP SEQUENCE IF EXISTS public.customer_category_id_seq;
DROP TABLE IF EXISTS public.customer_category;
DROP TABLE IF EXISTS public.customer;
DROP SEQUENCE IF EXISTS public.company_settings_id_seq;
DROP TABLE IF EXISTS public.company_settings;
DROP TYPE IF EXISTS public.supplierorderstatusenum;
DROP TYPE IF EXISTS public.quotationstatusenum;
DROP TYPE IF EXISTS public.quotation_status;
DROP TYPE IF EXISTS public.deliverystatusenum;
--
-- Name: deliverystatusenum; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.deliverystatusenum AS ENUM (
    'PENDING',
    'DELIVERED'
);


ALTER TYPE public.deliverystatusenum OWNER TO neondb_owner;

--
-- Name: quotation_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.quotation_status AS ENUM (
    'DRAFT',
    'SENT',
    'ACCEPTED',
    'REJECTED',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.quotation_status OWNER TO neondb_owner;

--
-- Name: quotationstatusenum; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.quotationstatusenum AS ENUM (
    'DRAFT',
    'SENT',
    'ACCEPTED',
    'REJECTED',
    'WORK_IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.quotationstatusenum OWNER TO neondb_owner;

--
-- Name: supplierorderstatusenum; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.supplierorderstatusenum AS ENUM (
    'NOT_ORDERED',
    'ORDERED',
    'RECEIVED'
);


ALTER TYPE public.supplierorderstatusenum OWNER TO neondb_owner;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: company_settings; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.company_settings (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    address_line1 character varying(255),
    address_line2 character varying(255),
    phone character varying(50),
    email character varying(100),
    website character varying(255),
    logo_path character varying(255),
    pdf_orientation character varying(20) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.company_settings OWNER TO neondb_owner;

--
-- Name: company_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.company_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_settings_id_seq OWNER TO neondb_owner;

--
-- Name: company_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.company_settings_id_seq OWNED BY public.company_settings.id;


--
-- Name: customer; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.customer (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100),
    phone character varying(20),
    address character varying(200),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    category_id integer
);


ALTER TABLE public.customer OWNER TO neondb_owner;

--
-- Name: customer_category; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.customer_category (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(200),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.customer_category OWNER TO neondb_owner;

--
-- Name: customer_category_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.customer_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_category_id_seq OWNER TO neondb_owner;

--
-- Name: customer_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.customer_category_id_seq OWNED BY public.customer_category.id;


--
-- Name: customer_contact; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.customer_contact (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    contact_date timestamp without time zone,
    contact_type character varying(50) NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.customer_contact OWNER TO neondb_owner;

--
-- Name: customer_contact_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.customer_contact_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_contact_id_seq OWNER TO neondb_owner;

--
-- Name: customer_contact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.customer_contact_id_seq OWNED BY public.customer_contact.id;


--
-- Name: customer_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.customer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_id_seq OWNER TO neondb_owner;

--
-- Name: customer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.customer_id_seq OWNED BY public.customer.id;


--
-- Name: file_upload; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.file_upload (
    id integer NOT NULL,
    filename character varying(255) NOT NULL,
    file_type character varying(20) NOT NULL,
    customer_id integer,
    upload_date timestamp without time zone,
    processed boolean,
    processing_notes text
);


ALTER TABLE public.file_upload OWNER TO neondb_owner;

--
-- Name: file_upload_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.file_upload_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.file_upload_id_seq OWNER TO neondb_owner;

--
-- Name: file_upload_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.file_upload_id_seq OWNED BY public.file_upload.id;


--
-- Name: import_log; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.import_log (
    id integer NOT NULL,
    filename text NOT NULL,
    import_type character varying(50) NOT NULL,
    success_count integer NOT NULL,
    failure_count integer NOT NULL,
    imported_by integer NOT NULL,
    created_at timestamp without time zone,
    status character varying(20) NOT NULL,
    error_message text,
    rollback_data text
);


ALTER TABLE public.import_log OWNER TO neondb_owner;

--
-- Name: import_log_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.import_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.import_log_id_seq OWNER TO neondb_owner;

--
-- Name: import_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.import_log_id_seq OWNED BY public.import_log.id;


--
-- Name: invoice; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.invoice (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    invoice_date date NOT NULL,
    total_amount double precision,
    file_path character varying(255),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    currency character varying(10)
);


ALTER TABLE public.invoice OWNER TO neondb_owner;

--
-- Name: invoice_addenda; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.invoice_addenda (
    id uuid NOT NULL,
    customer_id integer NOT NULL,
    invoice_number character varying(30) NOT NULL,
    period_from date NOT NULL,
    period_to date NOT NULL,
    status character varying(20) NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.invoice_addenda OWNER TO neondb_owner;

--
-- Name: invoice_addendum_lines; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.invoice_addendum_lines (
    id uuid NOT NULL,
    addendum_id uuid NOT NULL,
    sale_date date NOT NULL,
    quantity numeric(10,2) NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    vat_rate numeric(4,2) NOT NULL,
    notes text,
    created_at timestamp without time zone,
    product_name character varying(200) DEFAULT ''::character varying NOT NULL,
    product_category character varying(100),
    product_description text
);


ALTER TABLE public.invoice_addendum_lines OWNER TO neondb_owner;

--
-- Name: invoice_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.invoice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoice_id_seq OWNER TO neondb_owner;

--
-- Name: invoice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.invoice_id_seq OWNED BY public.invoice.id;


--
-- Name: invoice_item; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.invoice_item (
    id integer NOT NULL,
    invoice_id integer NOT NULL,
    product_id integer,
    description character varying(200) NOT NULL,
    quantity double precision NOT NULL,
    price double precision NOT NULL,
    vat double precision,
    total double precision,
    scientific_name character varying(150),
    pot_size character varying(50),
    vat_percentage double precision
);


ALTER TABLE public.invoice_item OWNER TO neondb_owner;

--
-- Name: invoice_item_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.invoice_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoice_item_id_seq OWNER TO neondb_owner;

--
-- Name: invoice_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.invoice_item_id_seq OWNED BY public.invoice_item.id;


--
-- Name: lead; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.lead (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    phone character varying(20),
    message text,
    source character varying(50),
    status character varying(20),
    items json,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    converted_to_quotation_id integer,
    quoter_draft_id character varying(100)
);


ALTER TABLE public.lead OWNER TO neondb_owner;

--
-- Name: lead_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.lead_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lead_id_seq OWNER TO neondb_owner;

--
-- Name: lead_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.lead_id_seq OWNED BY public.lead.id;


--
-- Name: order; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public."order" (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    order_number character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    delivery_date date,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public."order" OWNER TO neondb_owner;

--
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_id_seq OWNER TO neondb_owner;

--
-- Name: order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


--
-- Name: order_item; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.order_item (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer,
    plant_name character varying(200) NOT NULL,
    size character varying(50),
    quantity integer NOT NULL,
    price double precision NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    price_list_id integer,
    updated_price_list boolean DEFAULT false,
    vat_rate double precision DEFAULT 19.0 NOT NULL
);


ALTER TABLE public.order_item OWNER TO neondb_owner;

--
-- Name: order_item_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.order_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_item_id_seq OWNER TO neondb_owner;

--
-- Name: order_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.order_item_id_seq OWNED BY public.order_item.id;


--
-- Name: price_list; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.price_list (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    price double precision NOT NULL,
    effective_date date,
    expiry_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    source_file character varying(255)
);


ALTER TABLE public.price_list OWNER TO neondb_owner;

--
-- Name: price_list_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.price_list_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.price_list_id_seq OWNER TO neondb_owner;

--
-- Name: price_list_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.price_list_id_seq OWNED BY public.price_list.id;


--
-- Name: price_list_item; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.price_list_item (
    id integer NOT NULL,
    price_list_id integer NOT NULL,
    product_id integer,
    name character varying(200) NOT NULL,
    size character varying(50),
    price double precision NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.price_list_item OWNER TO neondb_owner;

--
-- Name: price_list_item_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.price_list_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.price_list_item_id_seq OWNER TO neondb_owner;

--
-- Name: price_list_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.price_list_item_id_seq OWNED BY public.price_list_item.id;


--
-- Name: product; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.product (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    sku character varying(50),
    description text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    category character varying(100),
    scientific_name character varying(150),
    pot character varying(50)
);


ALTER TABLE public.product OWNER TO neondb_owner;

--
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_id_seq OWNER TO neondb_owner;

--
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- Name: product_update_request; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.product_update_request (
    id integer NOT NULL,
    product_id integer NOT NULL,
    price_list_id integer,
    old_price double precision NOT NULL,
    new_price double precision NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    source_file character varying(255)
);


ALTER TABLE public.product_update_request OWNER TO neondb_owner;

--
-- Name: product_update_request_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.product_update_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_update_request_id_seq OWNER TO neondb_owner;

--
-- Name: product_update_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.product_update_request_id_seq OWNED BY public.product_update_request.id;


--
-- Name: quotation; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.quotation (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    quotation_number character varying(50) NOT NULL,
    quotation_date date NOT NULL,
    total_amount double precision,
    currency character varying(10) NOT NULL,
    notes text,
    file_path character varying(255),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    status character varying(20) DEFAULT 'created'::character varying,
    valid_until date,
    viewed_at timestamp without time zone,
    accepted_at timestamp without time zone,
    rejected_at timestamp without time zone,
    order_id character varying(50)
);


ALTER TABLE public.quotation OWNER TO neondb_owner;

--
-- Name: quotation_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.quotation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quotation_id_seq OWNER TO neondb_owner;

--
-- Name: quotation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.quotation_id_seq OWNED BY public.quotation.id;


--
-- Name: quotation_item; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.quotation_item (
    id integer NOT NULL,
    quotation_id integer NOT NULL,
    product_id integer,
    description character varying(200) NOT NULL,
    scientific_name character varying(150),
    pot_size character varying(50),
    quantity double precision NOT NULL,
    selling_price double precision NOT NULL,
    vat_rate double precision NOT NULL,
    supplier character varying(255),
    cost_price double precision,
    total double precision,
    height character varying(50),
    supplier_id integer,
    "position" integer DEFAULT 0,
    delivery_status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    supplier_order_status character varying(20) DEFAULT 'NOT_ORDERED'::character varying NOT NULL,
    delivery_date timestamp without time zone,
    supplier_order_date timestamp without time zone,
    supplier_order_reference character varying(100)
);


ALTER TABLE public.quotation_item OWNER TO neondb_owner;

--
-- Name: quotation_item_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.quotation_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quotation_item_id_seq OWNER TO neondb_owner;

--
-- Name: quotation_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.quotation_item_id_seq OWNED BY public.quotation_item.id;


--
-- Name: supplier; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.supplier (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    contact_person character varying(100),
    email character varying(100),
    phone character varying(50),
    address character varying(255),
    notes text,
    is_inhouse boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.supplier OWNER TO neondb_owner;

--
-- Name: supplier_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.supplier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.supplier_id_seq OWNER TO neondb_owner;

--
-- Name: supplier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.supplier_id_seq OWNED BY public.supplier.id;


--
-- Name: supplier_product; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.supplier_product (
    id integer NOT NULL,
    supplier_id integer NOT NULL,
    product_name character varying(255) NOT NULL,
    scientific_name character varying(150),
    height character varying(50),
    pot_size character varying(50),
    price double precision NOT NULL,
    cost_price double precision,
    last_detected timestamp without time zone,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    flagged_duplicate boolean DEFAULT false
);


ALTER TABLE public.supplier_product OWNER TO neondb_owner;

--
-- Name: supplier_product_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.supplier_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.supplier_product_id_seq OWNER TO neondb_owner;

--
-- Name: supplier_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.supplier_product_id_seq OWNED BY public.supplier_product.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    password_hash character varying(256) NOT NULL,
    is_admin boolean,
    created_at timestamp without time zone,
    last_login timestamp without time zone
);


ALTER TABLE public."user" OWNER TO neondb_owner;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO neondb_owner;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: company_settings id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_settings ALTER COLUMN id SET DEFAULT nextval('public.company_settings_id_seq'::regclass);


--
-- Name: customer id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer ALTER COLUMN id SET DEFAULT nextval('public.customer_id_seq'::regclass);


--
-- Name: customer_category id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer_category ALTER COLUMN id SET DEFAULT nextval('public.customer_category_id_seq'::regclass);


--
-- Name: customer_contact id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer_contact ALTER COLUMN id SET DEFAULT nextval('public.customer_contact_id_seq'::regclass);


--
-- Name: file_upload id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.file_upload ALTER COLUMN id SET DEFAULT nextval('public.file_upload_id_seq'::regclass);


--
-- Name: import_log id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.import_log ALTER COLUMN id SET DEFAULT nextval('public.import_log_id_seq'::regclass);


--
-- Name: invoice id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice ALTER COLUMN id SET DEFAULT nextval('public.invoice_id_seq'::regclass);


--
-- Name: invoice_item id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_item ALTER COLUMN id SET DEFAULT nextval('public.invoice_item_id_seq'::regclass);


--
-- Name: lead id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.lead ALTER COLUMN id SET DEFAULT nextval('public.lead_id_seq'::regclass);


--
-- Name: order id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);


--
-- Name: order_item id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item ALTER COLUMN id SET DEFAULT nextval('public.order_item_id_seq'::regclass);


--
-- Name: price_list id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list ALTER COLUMN id SET DEFAULT nextval('public.price_list_id_seq'::regclass);


--
-- Name: price_list_item id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list_item ALTER COLUMN id SET DEFAULT nextval('public.price_list_item_id_seq'::regclass);


--
-- Name: product id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- Name: product_update_request id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product_update_request ALTER COLUMN id SET DEFAULT nextval('public.product_update_request_id_seq'::regclass);


--
-- Name: quotation id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation ALTER COLUMN id SET DEFAULT nextval('public.quotation_id_seq'::regclass);


--
-- Name: quotation_item id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation_item ALTER COLUMN id SET DEFAULT nextval('public.quotation_item_id_seq'::regclass);


--
-- Name: supplier id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.supplier ALTER COLUMN id SET DEFAULT nextval('public.supplier_id_seq'::regclass);


--
-- Name: supplier_product id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.supplier_product ALTER COLUMN id SET DEFAULT nextval('public.supplier_product_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: company_settings; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.company_settings (id, name, address_line1, address_line2, phone, email, website, logo_path, pdf_orientation, created_at, updated_at) FROM stdin;
1	Andreas Pakkoutis & Sons Ltd	Griva Digeni 39	Avgorou 5510	23922394	panayiotis@pakkoutis.com	\N	/tmp/uploads/logo_cad23205_pakkoutis_Company_Logo.png	landscape	2025-04-03 10:53:18.563897	2025-05-28 15:25:51.940733
\.


--
-- Data for Name: customer; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.customer (id, name, email, phone, address, created_at, updated_at, category_id) FROM stdin;
42	Γιάννης Μάστρου	\N	99133684	Λιοπέτρι	2025-05-22 17:38:11.911152	2025-05-28 18:12:59.526395	9
40	Stavros Andronikou and Son (Construction) Ltd	info@saconstruction.cy	96300907	\N	2025-05-19 13:09:39.727124	2025-05-28 18:13:13.275362	8
43	Ανδρέας Μάστρου	\N	97616544	Λιοπέτρι	2025-05-23 15:27:04.805671	2025-05-28 18:13:28.686085	8
44	Φυτώριο Νεοφυτα	\N	\N	Χοιροκιτια	2025-05-26 09:28:29.471949	2025-05-28 18:13:42.482468	10
38	Giagkos Garden Services Ltd		99043772		2025-05-18 09:28:29.29572	2025-05-18 09:28:29.295731	7
1	Greentouch	\N	\N	\N	2025-04-01 08:13:00.442652	2025-05-28 18:03:32.050397	7
2	Chrymaris	\N	\N	\N	2025-04-01 15:48:20.287978	2025-05-28 18:03:55.632253	7
9	Μάριος Μιχάηλ	\N	\N	Σωτήρα	2025-04-02 16:20:34.499593	2025-05-28 18:04:53.517856	7
4	Soteris Shaelos Plants	\N	\N	\N	2025-04-01 18:30:41.457706	2025-05-28 18:05:13.565178	7
5	Solomou Gardens	\N	\N	\N	2025-04-01 18:35:03.686453	2025-05-28 18:05:30.68393	7
6	LP IDEAL PROPERTIES LTD	\N	\N	\N	2025-04-01 18:38:50.483723	2025-05-28 18:05:51.327011	8
7	Μηνάς Μωυσέως & Ανδρέας Λουκά	\N	\N	\N	2025-04-01 19:55:00.704507	2025-05-28 18:06:21.8966	7
8	Φυτώριο Ο Πράσινος Κόσμος	\N	\N	\N	2025-04-02 11:35:40.571103	2025-05-28 18:06:58.46685	8
10	N.C.P. CHRISTOU LTD	\N	\N	\N	2025-04-04 14:47:37.224033	2025-05-28 18:07:12.148158	10
3	Ordinatio	\N	\N	\N	2025-04-01 18:26:43.176216	2025-05-28 18:07:28.875831	7
11	BEGONIA GARDENS	\N	\N	\N	2025-04-04 15:26:38.646953	2025-05-28 18:07:40.510575	10
12	BLUMECO GARDEN CENTER	\N	\N	\N	2025-04-04 15:31:59.815237	2025-05-28 18:07:59.508463	10
14	Gardens etc	\N	\N	\N	2025-04-06 14:01:30.0023	2025-05-28 18:08:17.408172	10
20	Κώστας Αθανασίου	\N	99942765	Φρέναρος	2025-04-07 17:25:28.442781	2025-05-28 18:08:34.891785	8
21	K.T. Purple Developers	\N	\N	\N	2025-04-09 12:10:58.651331	2025-05-28 18:08:53.167909	8
23	A. L. Landscape & Garden Maint. Ltd	\N	\N	\N	2025-04-11 17:57:30.144307	2025-05-28 18:09:07.435185	7
24	Μιχάλης Νικολάου	michalis2106@gmail.com	99449018	Λαρνακα	2025-04-14 15:47:50.893718	2025-05-28 18:09:25.284329	9
25	IVR IMAGINE VILLA RENTALS LTD	\N	\N	\N	2025-04-15 11:22:35.057389	2025-05-28 18:09:38.363268	8
15	ΔΗΜΟΤΙΚΟ ΣΧΟΛΕΙΟ ΠΡΟΔΡΟΜΟΥ	\N	\N	\N	2025-04-06 17:23:25.242354	2025-05-28 18:09:58.869768	9
33	Ιερά Μονή Αβακούμ	\N	\N	\N	2025-04-27 07:22:40.716185	2025-05-28 18:10:15.100334	9
34	Δήμος Αγίας Νάπας - Δημοτικό διαμέρισμα Αγίας Νάπας	\N	\N	\N	2025-04-29 12:38:14.144086	2025-05-28 18:10:35.723522	8
35	Δήμος Παραλιμνίνου - Δερύνειας	\N	\N	\N	2025-05-03 13:13:23.59342	2025-05-28 18:10:56.683966	8
36	Γιώργος Τουμάζος	agrogarden.services@gmail.com	97737394	Πύλα	2025-05-09 16:33:02.79036	2025-05-28 18:11:12.293482	8
37	ΔΗΜΟΤΙΚΟ ΣΧΟΛΕΙΟ ΑΥΓΟΡΟΥ ΄Β	\N	\N	\N	2025-05-15 12:41:23.795828	2025-05-28 18:11:26.979162	9
13	K.S. FLOWERSHOP COMPANY LTD	flowercy@primehome.com	99425997	\N	2025-04-06 12:55:25.594357	2025-05-28 18:11:45.777878	10
39	Antonis Christou (Jello)	\N	99418980	\N	2025-05-19 09:40:23.187821	2025-05-28 18:12:30.327121	9
41	Κώστας Χριστοδούλου Λτδ	\N	99479307	\N	2025-05-22 08:56:58.582298	2025-05-28 18:12:42.240844	10
45	Φυτώρια Παναγιώτου	\N	\N	\N	2025-05-28 18:39:58.871637	2025-05-28 18:39:58.871642	7
\.


--
-- Data for Name: customer_category; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.customer_category (id, name, description, created_at, updated_at) FROM stdin;
1	General	Default category for customers	2025-04-06 17:19:39.354797	2025-04-06 17:19:39.354801
5	Test Category	For testing	2025-04-06 17:29:57.103414	2025-04-06 17:29:57.103418
7	Gardeners A	Professional gardeners with frequent and large-scale orders. Prioritize consistency, quality, and reliable service.	2025-04-16 19:38:49.527754	2025-04-16 19:38:49.527757
8	Gardeners B		2025-05-28 18:02:42.873006	2025-05-28 18:02:42.87301
9	Retailers		2025-05-28 18:03:00.915368	2025-05-28 18:03:00.915371
10	Shops		2025-05-28 18:06:42.227842	2025-05-28 18:06:42.227846
\.


--
-- Data for Name: customer_contact; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.customer_contact (id, customer_id, contact_date, contact_type, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: file_upload; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.file_upload (id, filename, file_type, customer_id, upload_date, processed, processing_notes) FROM stdin;
1	Greentouch.xlsx	excel	1	2025-04-01 08:13:41.868737	f	Error processing file: Missing optional dependency 'openpyxl'.  Use pip or conda to install openpyxl.
2	Customer_Invoice_1541.pdf	pdf	1	2025-04-01 08:14:38.980067	f	\N
3	Customer_Invoice_1541.pdf	pdf	1	2025-04-01 08:15:46.634246	t	Successfully processed. Created invoice #1541 with 2 items.
4	Greentouch.xlsx	excel	1	2025-04-01 08:17:02.891289	f	Error processing file: Missing required column: 'Name'
5	Greentouch.xlsx	excel	1	2025-04-01 08:18:50.871379	f	Error processing file: Missing required column: 'Name'
6	Greentouch.xlsx	excel	1	2025-04-01 08:20:10.67878	f	\N
7	Greentouch.xlsx	excel	1	2025-04-01 08:23:19.669186	f	\N
8	Greentouch.xlsx	excel	1	2025-04-01 09:31:31.654956	f	\N
9	Greentouch.xlsx	excel	1	2025-04-01 09:34:25.290407	t	Processed with errors: Error parsing Excel file: Missing required column: 'Name'
10	Greentouch.xlsx	excel	1	2025-04-01 09:34:56.736004	t	Processed with errors: Error parsing Excel file: Missing required column: 'Name'
11	price_list_template.xlsx	excel	1	2025-04-01 15:44:38.022134	t	Successfully processed. Added 102 products and 103 price list entries.
12	price_list_template.xlsx	excel	2	2025-04-01 15:51:29.401488	f	\N
13	price_list_template.xlsx	excel	2	2025-04-01 15:55:15.943322	f	\N
14	price_list_template.xlsx	excel	2	2025-04-01 15:55:49.830734	f	\N
15	price_list_template.xlsx	excel	2	2025-04-01 16:15:04.389146	f	\N
16	price_list_template2.xlsx	excel	2	2025-04-01 16:16:40.254158	f	\N
17	price_list_template2.xlsx	excel	2	2025-04-01 16:21:51.431011	f	\N
18	price_list_template2.xlsx	excel	2	2025-04-01 16:27:58.676125	f	\N
19	price_list_template2.xlsx	excel	2	2025-04-01 16:34:03.477134	f	\N
20	price_list_template2.xlsx	excel	2	2025-04-01 17:02:46.53638	f	\N
21	price_list_template2.xlsx	excel	2	2025-04-01 17:04:42.207405	f	\N
22	price_list_template2.xlsx	excel	2	2025-04-01 17:12:26.142584	f	\N
23	price_list_template2.xlsx	excel	2	2025-04-01 17:13:05.864227	f	\N
24	price_list_template1.xlsx	excel	2	2025-04-01 17:16:56.80066	t	Successfully processed. Added 43 products and 81 price list entries.
25	1503.pdf	pdf	2	2025-04-01 17:36:38.957634	t	Successfully processed. Created invoice #1503 with 2 items.
26	price_list_template1.xlsx	excel	3	2025-04-01 18:27:57.030929	t	Successfully processed. Added 11 products and 55 price list entries.
27	price_list_template1.xlsx	excel	4	2025-04-01 18:31:07.569747	t	Successfully processed. Added 7 products and 41 price list entries.
28	price_list_template1.xlsx	excel	5	2025-04-01 18:35:37.898084	t	Successfully processed. Added 36 products and 153 price list entries.
29	1551.pdf	pdf	6	2025-04-01 18:39:22.624385	t	Successfully processed. Created invoice #1551 with 4 items.
30	1551.pdf	pdf	6	2025-04-01 18:56:30.079993	f	\N
31	1201.pdf	pdf	6	2025-04-01 18:56:54.865892	t	Successfully processed. Created invoice #1201 with 2 items.
32	1184_1.pdf	pdf	6	2025-04-01 19:02:15.900862	t	Successfully processed. Created invoice #1184 with 3 items.
33	1551.pdf	pdf	6	2025-04-01 19:31:04.679733	t	Successfully processed. Created invoice #1551 with 4 items. Also created 4 new price list entries.
42	1458_1.pdf	pdf	7	2025-04-01 20:28:38.220031	t	Successfully processed. Created invoice #1458 with 18 items. Also added 1 pending price updates.
34	1184_1.pdf	pdf	6	2025-04-01 19:32:20.148069	t	Successfully processed. Created invoice #1184 with 3 items. Also added 3 pending price updates.
35	889_1.pdf	pdf	7	2025-04-01 19:55:25.646122	t	Successfully processed. Created invoice #889 with 2 items. Also created 2 new price list entries.
43	1458_1.pdf	pdf	7	2025-04-01 20:33:21.445498	t	Successfully processed. Created invoice #1458 with 18 items. Also added 1 pending price updates.
36	890_1.pdf	pdf	7	2025-04-01 19:55:44.420393	t	Successfully processed. Created invoice #890 with 5 items. Also created 5 new price list entries.
37	1112_1.pdf	pdf	7	2025-04-01 19:56:03.816669	t	Successfully processed. Created invoice #1112 with 3 items. Also created 3 new price list entries.
44	1458_1.pdf	pdf	7	2025-04-01 20:37:00.278817	t	Successfully processed. Created invoice #1458 with 18 items. Also added 1 pending price updates.
38	1302_1.pdf	pdf	7	2025-04-01 19:57:02.325694	t	Successfully processed. Created invoice #1302 with 10 items. Also created 9 new price list entries.
39	1381_1.pdf	pdf	7	2025-04-01 19:57:21.593759	t	Successfully processed. Created invoice #1381 with 8 items. Also created 5 new price list entries.
40	1458_1.pdf	pdf	7	2025-04-01 19:57:42.740361	t	Successfully processed. Created invoice #1458 with 18 items. Also created 13 new price list entries and added 3 pending price updates.
41	1458_1.pdf	pdf	7	2025-04-01 20:21:51.734499	t	Successfully processed. Created invoice #1458 with 18 items. Also created 2 new price list entries and added 1 pending price updates.
45	1552.pdf	pdf	4	2025-04-02 11:30:11.15489	t	Successfully processed. Created invoice #1552 with 2 items. Also created 2 new price list entries.
46	1553.pdf	pdf	8	2025-04-02 11:36:04.439726	t	Successfully processed. Created invoice #1553 with 0 items.
51	1566.pdf	pdf	10	2025-04-04 14:50:58.761265	t	Successfully processed. Created invoice #1566 with 22 items. Also created 22 new price list entries.
47	1553.pdf	pdf	8	2025-04-02 11:46:34.314812	t	Successfully processed. Created invoice #1553 with 0 items.
48	1553.pdf	pdf	8	2025-04-02 12:18:26.985583	t	Successfully processed. Created invoice #1553 with 0 items.
52	Customer_Invoice_1566.xlsx	customer_invoice	10	2025-04-04 14:54:29.35651	t	Successfully processed. Updated 0 existing prices and added 23 new price list entries.
49	1553.pdf	pdf	8	2025-04-02 12:25:47.633371	t	Successfully processed. Created invoice #1553 with 1 items. Also created 1 new price list entries.
50	Customer_Invoice_1566.xlsx	customer_invoice	10	2025-04-04 14:47:59.645674	t	No product data found in the invoice file.
53	Customer_Invoice_1566.xlsx	customer_invoice	10	2025-04-04 15:03:00.601964	t	Successfully processed. Updated 0 existing prices and added 8 new price list entries.
54	Customer_Invoice_1566.xlsx	customer_invoice	10	2025-04-04 15:17:40.958868	t	Successfully processed. Updated 0 existing prices and added 25 new price list entries.
55	1412.xlsx	customer_invoice	11	2025-04-04 15:26:56.032468	t	Successfully processed. Updated 0 existing prices and added 16 new price list entries.
56	1484.xlsx	customer_invoice	11	2025-04-04 15:27:12.603208	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
57	1512.xlsx	customer_invoice	11	2025-04-04 15:27:25.350805	t	Successfully processed. Updated 0 existing prices and added 16 new price list entries.
58	1561.xlsx	customer_invoice	11	2025-04-04 15:27:43.853509	t	Successfully processed. Updated 0 existing prices and added 7 new price list entries.
59	1060.xlsx	customer_invoice	12	2025-04-04 15:32:14.817081	t	Successfully processed. Updated 0 existing prices and added 7 new price list entries.
60	1146.xlsx	customer_invoice	12	2025-04-04 15:32:37.591568	t	Successfully processed. Updated 0 existing prices and added 6 new price list entries.
61	1170.xlsx	customer_invoice	11	2025-04-04 15:32:52.181664	t	No product data found in the invoice file.
62	1170.xlsx	customer_invoice	12	2025-04-04 15:34:32.367723	t	Successfully processed. Updated 0 existing prices and added 7 new price list entries.
63	1383.xlsx	customer_invoice	12	2025-04-04 15:34:56.607268	t	Successfully processed. Updated 0 existing prices and added 2 new price list entries.
64	1417.xlsx	customer_invoice	12	2025-04-04 15:35:14.725297	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
65	1570.xlsx	customer_invoice	13	2025-04-06 12:55:44.14896	t	Successfully processed. Updated 0 existing prices and added 3 new price list entries.
66	1571.xlsx	customer_invoice	12	2025-04-06 13:01:50.290465	t	Successfully processed. Updated 0 existing prices and added 4 new price list entries.
67	1572.xlsx	customer_invoice	4	2025-04-06 13:42:42.555589	t	Successfully processed. Updated 0 existing prices and added 2 new price list entries.
68	1575.xlsx	customer_invoice	14	2025-04-06 14:01:54.070751	t	Successfully processed. Updated 0 existing prices and added 4 new price list entries.
69	1576.xlsx	customer_invoice	2	2025-04-06 14:17:39.52189	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
70	1584.xlsx	customer_invoice	2	2025-04-07 14:51:55.933509	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
71	0001.xlsx	customer_invoice	2	2025-04-08 13:20:39.551957	t	Successfully processed. Updated 3 existing prices and added 7 new price list entries.
72	1117.xlsx	customer_invoice	2	2025-04-08 13:27:56.693058	t	Successfully processed. Updated 0 existing prices and added 3 new price list entries.
73	1147.xlsx	customer_invoice	2	2025-04-08 13:28:07.016458	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
74	1167.xlsx	customer_invoice	2	2025-04-08 13:28:17.683625	t	Successfully processed. Updated 1 existing prices and added 3 new price list entries.
75	1271.xlsx	customer_invoice	2	2025-04-08 13:28:28.274816	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
76	1289.xlsx	customer_invoice	2	2025-04-08 13:28:38.037953	t	Successfully processed. Updated 1 existing prices and added 2 new price list entries.
77	1289.xlsx	customer_invoice	2	2025-04-08 13:28:48.365337	t	Successfully processed. Updated 2 existing prices and added 0 new price list entries.
78	1310.xlsx	customer_invoice	2	2025-04-08 13:28:58.172628	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
79	1429.xlsx	customer_invoice	2	2025-04-08 13:29:11.581043	t	Successfully processed. Updated 0 existing prices and added 0 new price list entries.
80	1448.xlsx	customer_invoice	2	2025-04-08 13:29:25.755225	t	Successfully processed. Updated 0 existing prices and added 2 new price list entries.
81	1587.xlsx	customer_invoice	2	2025-04-08 13:34:50.306391	t	No product data found in the invoice file.
82	1587.xlsx	customer_invoice	2	2025-04-08 13:35:49.190097	t	Successfully processed. Updated 2 existing prices and added 1 new price list entries.
83	967.xlsx	customer_invoice	21	2025-04-09 12:11:32.565842	t	Successfully processed. Updated 0 existing prices and added 13 new price list entries.
84	1367.xlsx	customer_invoice	21	2025-04-09 12:11:50.613209	t	Successfully processed. Updated 1 existing prices and added 3 new price list entries.
85	1370.xlsx	customer_invoice	21	2025-04-09 12:12:07.908541	t	Successfully processed. Updated 0 existing prices and added 1 new price list entries.
86	1593.xlsx	customer_invoice	1	2025-04-10 13:52:57.874039	t	No product data found in the invoice file.
87	1596.xlsx	customer_invoice	10	2025-04-11 15:50:17.113061	t	No product data found in the invoice file.
88	1596.pdf	pdf	10	2025-04-11 15:51:46.879403	t	Successfully processed. Created invoice #1596 with 12 items. Also created 12 new price list entries.
89	1604.xlsx	customer_invoice	4	2025-04-14 16:26:10.73505	t	Successfully processed. Updated 0 existing prices and added 2 new price list entries.
90	1617.xlsx	customer_invoice	5	2025-04-17 16:37:01.45284	t	No product data found in the invoice file.
91	1617.xlsx	customer_invoice	5	2025-04-17 16:38:30.234765	t	No product data found in the invoice file.
92	1617.xls	customer_invoice	5	2025-04-17 16:39:10.666752	t	Error processing customer invoice: openpyxl does not support the old .xls file format, please use xlrd to read this file, or convert it to the more recent .xlsx file format.
93	1617.pdf	pdf	5	2025-04-17 16:39:34.599853	f	\N
94	1617.pdf	pdf	5	2025-04-17 16:40:21.353148	f	\N
95	1617.xlsx	customer_invoice	5	2025-04-17 16:45:36.133618	t	No product data found in the invoice file.
96	1507.xlsx	customer_invoice	34	2025-04-29 12:38:41.383321	t	Successfully processed. Updated 0 existing prices and added 5 new price list entries.
97	1648.xlsx	customer_invoice	34	2025-04-29 12:55:19.482042	t	Successfully processed. Updated 1 existing prices and added 8 new price list entries.
\.


--
-- Data for Name: import_log; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.import_log (id, filename, import_type, success_count, failure_count, imported_by, created_at, status, error_message, rollback_data) FROM stdin;
\.


--
-- Data for Name: invoice; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.invoice (id, customer_id, invoice_number, invoice_date, total_amount, file_path, created_at, updated_at, currency) FROM stdin;
\.


--
-- Data for Name: invoice_addenda; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.invoice_addenda (id, customer_id, invoice_number, period_from, period_to, status, notes, created_at, updated_at) FROM stdin;
6795a2fe-747f-432e-93db-ec8e240dd061	34	test01	2025-02-01	2025-05-30	draft	This is a test addendum	2025-05-28 13:51:54.040715	2025-05-28 13:51:54.040718
d070cbe5-db8d-4f73-b4b3-398f56606821	34	252525	2025-01-01	2025-05-28	draft	τεστ	2025-05-28 14:13:39.330302	2025-05-28 14:13:39.330304
4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	34	1742	2025-01-01	2025-05-28	locked		2025-05-28 14:34:06.771847	2025-05-28 16:18:58.567462
\.


--
-- Data for Name: invoice_addendum_lines; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.invoice_addendum_lines (id, addendum_id, sale_date, quantity, unit_price, vat_rate, notes, created_at, product_name, product_category, product_description) FROM stdin;
d931e123-22a2-4acf-b80f-171f8010aa01	6795a2fe-747f-432e-93db-ec8e240dd061	2025-02-02	1.00	15.00	19.00		2025-05-28 14:00:28.492972	Στεφάνι		Κηδεία Αδελφής Α. Λιμνιώτη
a7575663-f273-4bed-ba6b-a526141e6744	6795a2fe-747f-432e-93db-ec8e240dd061	2025-02-13	1.00	15.00	19.00		2025-05-28 14:01:22.124335	Στεφάνι		Κηδείας Γιώτα Μουστάκα
24c72943-bf19-457a-a840-02075f365298	d070cbe5-db8d-4f73-b4b3-398f56606821	2025-01-08	1.00	15.00	19.00		2025-05-28 14:16:42.393895	Στεφάνι		Κηδεία Αδελφής Α. Λιμνιώτη
0a7b5d8a-c5a6-4e12-ade2-afe7721f8dbb	d070cbe5-db8d-4f73-b4b3-398f56606821	2025-01-13	1.00	15.00	19.00		2025-05-28 14:17:22.154998	Στεφάνι		Κηδείας Γιώτη Μουστάκα
e56132b3-83f7-44b6-aa84-50ba84c81cba	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-01-08	1.00	12.61	19.00		2025-05-28 14:36:09.833449	Στεφάνι		Κηδεία Αδελφής Α. Λιμνιώτη
64cc5db2-e9d2-4a4f-b3e9-e8f81d34adbc	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-01-13	1.00	12.61	19.00		2025-05-28 14:38:47.163666	Στεφάνι		Κηδεία Γιώτας Μουστακά
c154547d-be45-4098-8cff-5f6e6cd669d9	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-01-14	1.00	12.61	19.00		2025-05-28 14:41:21.033106	Στεφάνι		Κηδεία Πάτερ Τρύφωνα
6b683ef3-1c82-4427-a0df-34da83ed041c	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-01-14	1.00	12.61	19.00		2025-05-28 14:42:47.571976	Στεφάνι		Κηδεία Πάτερ Τρύφωνα, Δήμος Αγίας Νάπας, κος Χρ. Ζαννέτος
f13e84dc-5b45-4541-a9f6-d8dad82999c2	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-02-12	1.00	12.61	19.00		2025-05-28 14:43:52.377011	Στεφάνι		Κηδεία Μαρίας Ν. Ζήσιμου
fa40f18f-ea8f-41e2-87b6-01d8626a4870	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-02-19	1.00	12.61	19.00		2025-05-28 14:44:48.420714	Στεφάνι		Κηδεία Λοϊζου Ιωακείμ
402c6b09-21bd-43ed-a2be-a5c5112e3dbf	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-02-22	1.00	5.88	19.00		2025-05-28 14:46:24.658655	Φυτό		Μνημόσυνο Κυπριανού
5949d183-6e92-4be8-bc93-e6f17b313d78	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-07	1.00	12.61	19.00		2025-05-28 14:47:24.33548	Στεφάνι		Κηδεία Κας Καλλιόπης
c48b87b4-6404-40eb-b12c-bb4a052e6159	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-10	6.00	12.61	19.00		2025-05-28 14:50:08.037788	Ορθόκλονα κυπαρίσσια		Παρέλαβε ο κ. Παράσχος Φεσά
638b5905-e15e-4d65-be64-42459c612abb	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-12	1.00	12.61	19.00		2025-05-28 14:50:58.338601	Στεφάνι		Κηδεία Παλλούρα
66b974f2-74f3-4e36-9985-e0a4a66c9dea	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-08	2.00	12.61	19.00		2025-05-28 14:52:04.494173	Στεφάνι		Κηδεία Γ. Τσιολάκκης - Χριστούλα Αρτέμη
bcd30f81-cec1-42e4-975e-b1425e990bad	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-17	1.00	12.61	19.00		2025-05-28 14:53:51.996623	Στεφάνι		Κηδεία Κημελή Π. Τρόκκου
4646567d-5930-4257-8c12-902bb66f30d8	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-01	2.00	8.40	19.00		2025-05-28 14:55:07.72812	Δάφνινο Στεφάνι		
08aa1016-c0bd-40d9-a492-55f27b093db2	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-01	4.00	5.88	19.00		2025-05-28 14:55:42.012434	Δάφνινο Στεφάνι		Διά αναπαράσταση
aece8bcd-8527-4ab2-989a-600eeb0ab905	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-01-01	1.00	12.61	19.00		2025-05-28 14:56:22.581609	Στεφάνι		Κηδεία Μαρίας Χαραλάμπους
21f6193a-1747-4669-b5db-5dd2a268c270	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-01-22	1.00	12.61	19.00		2025-05-28 14:57:22.160511	Στεφάνι		Κηδείας νέου εις Αθηένου
ab9ee6d5-085d-4d0b-aed1-95fb595b4bd1	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-02-08	1.00	12.61	19.00		2025-05-28 14:58:14.696059	Στεφάνι		Κηδεία Γιάννη Ελευθερίου
64a65aeb-9df2-4b9b-8a9b-af239a5851b5	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-02-10	1.00	12.61	19.00		2025-05-28 15:01:10.632863	Στεφάνι		Κηδεία Λαμπρή Κλατσιά
088d8db7-74bc-40ee-bf8f-8a590f3a0bc1	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-02-21	1.00	25.21	19.00		2025-05-28 15:02:10.907799	Στεφάνι		Κηδεία εις Βρυσούλες
d35778d0-3244-4185-8b44-239b579036c3	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-02-26	1.00	12.61	19.00		2025-05-28 15:04:11.425604	Στεφάνι		Κηδεία Μαρίας Κόκου Μαργάρη
25aade06-c2d9-48e1-8c93-889cc2b604ce	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-01	1.00	12.61	19.00		2025-05-28 15:05:41.663064	Στεφάνι		Κηδεία Φτεροπουλλη Δημήτρης Αντρέου
3bdbc983-981f-4e1a-92f8-da33ce33c8ee	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-06	1.00	12.61	19.00		2025-05-28 15:06:32.400917	Στεφάνι		Κηδεία εις Ορμήδεια
c669790a-0b79-422b-bed0-41c95f1c523d	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-08	1.00	10.92	19.00		2025-05-28 15:07:45.101384	Φυτό		Μνημόσυνο Κούττα
dd6cc029-1f88-4a34-bd75-9914ae5fecea	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-24	1.00	8.40	19.00		2025-05-28 15:08:33.194749	Δάφνινο Στεφάνι		
fcbaf34e-6ea3-471f-bff3-a15e413b523d	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-03-22	4.00	8.40	19.00		2025-05-28 15:09:00.51959	Δάφνινο Στεφάνι		
07298247-eb91-4a9c-aa51-d94e232aed9a	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-05-07	2.00	25.21	19.00		2025-05-28 15:10:23.949874	Στεφάνι		Κηδεία Αδάμου Πατσαλή Λάρνακα
c1020608-e5b3-4908-a1a9-d6d427a080d0	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-05-15	1.00	25.21	19.00		2025-05-28 15:11:07.511638	Στεφάνι		Κηδεία Παρασκευά Ζορλή
da1b93ac-401c-488a-beb0-f2f6b4ae5b2d	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-05-22	1.00	12.61	19.00		2025-05-28 15:11:51.100852	Στεφάνι		Κηδεία Θέκλα Μάντολες
2b14bfdd-0e73-4828-a808-defaf940d383	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-12	3.00	25.21	19.00		2025-05-28 15:12:37.10454	Στεφάνι		Κηδεία Στέλλας Κάσια Παναγή
b7454e6c-7983-4a3a-9d24-c425e64cd3a0	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-11	1.00	12.61	19.00		2025-05-28 15:13:17.221243	Στεφάνι		Κηδεία Σαββάκη Ιωάννου
ab3c4039-f6a6-4adb-91af-18f311df9950	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-16	1.00	25.21	19.00		2025-05-28 15:14:22.308578	Στεφάνι		Κηδεία Σπύρου (γαμπρού) Χοιρίδη
047fe077-0941-4c74-bd89-f83119e4bef3	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-26	2.00	12.61	19.00		2025-05-28 15:15:14.667536	Στεφάνι		Παναγής Μιχαηλάς και Χρίστος Ζανέττος
8b10ee19-a8ef-4ef8-a0ef-86585f5ea053	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-30	1.00	12.61	19.00		2025-05-28 15:16:28.173393	Στεφάνι		Κηδεία Χριστ. Χριστοδούλου - Αντιδήμαρχος
6d8902ae-4ef0-45f0-8863-c2913be28d6e	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-04-30	1.00	25.21	19.00		2025-05-28 15:17:04.033833	Στεφάνι		Κηδεία Χριστ. Χριστοδούλου - Δήμαρχος
392e007b-dbb5-49a2-b77b-33246e2e56b0	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-05-05	1.00	12.61	19.00		2025-05-28 15:17:38.980634	Στεφάνι		Κηδεία Θεοδώρα Παναγή Σταυρή
75bf781d-91f3-40e2-bbe9-35a9cd0d4813	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-05-06	1.00	12.61	19.00		2025-05-28 15:18:09.326448	Στεφάνι		Κηδεία Γιωργή
d132cf81-ec48-4a09-a9a6-e8e061f203bc	4b6abdf6-ffbe-4b81-ae18-6a3bd048026a	2025-05-24	1.00	12.61	19.00		2025-05-28 15:18:48.844225	Στεφάνι		Κηδεία Παναγιώτας Καπά
\.


--
-- Data for Name: invoice_item; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.invoice_item (id, invoice_id, product_id, description, quantity, price, vat, total, scientific_name, pot_size, vat_percentage) FROM stdin;
\.


--
-- Data for Name: lead; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.lead (id, name, email, phone, message, source, status, items, created_at, updated_at, converted_to_quotation_id, quoter_draft_id) FROM stdin;
\.


--
-- Data for Name: order; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public."order" (id, customer_id, order_number, status, delivery_date, notes, created_at, updated_at) FROM stdin;
2	37	ORD-2025-002	cancelled	2025-05-27		2025-05-21 19:54:01.985888	2025-05-22 07:19:41.38682
5	42	ORD-2025-005	delivered	2025-05-24		2025-05-22 17:38:57.51963	2025-05-24 13:46:11.059397
3	1	ORD-2025-003	delivered	2025-05-24		2025-05-22 08:13:29.797243	2025-05-24 13:47:16.791791
1	37	ORD-2025-001	preparing	2025-05-27		2025-05-21 19:51:30.269171	2025-05-24 13:48:06.84602
6	43	ORD-2025-006	preparing	2025-05-30	Θα τα παραλάβει από τα φυτώρια	2025-05-23 15:27:41.276876	2025-05-25 08:53:34.318756
8	1	ORD-2025-008	new	2025-05-31		2025-05-26 14:46:16.185513	2025-05-26 14:46:16.185518
4	41	ORD-2025-004	delivered	2025-05-27	Called Doras from Monday 	2025-05-22 08:59:53.94988	2025-05-28 18:18:21.29516
7	44	ORD-2025-007	delivered	2025-05-30		2025-05-26 09:29:13.073518	2025-05-28 18:19:10.963944
\.


--
-- Data for Name: order_item; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.order_item (id, order_id, product_id, plant_name, size, quantity, price, notes, created_at, updated_at, price_list_id, updated_price_list, vat_rate) FROM stdin;
1	2	1834	Λαντάνα	2L	15	3	\N	2025-05-21 20:02:56.289332	2025-05-21 20:02:56.289336	\N	f	19
2	2	1775	Καρυ  2L	2L	1	1.25	\N	2025-05-22 07:01:14.398766	2025-05-22 07:01:14.398768	\N	f	19
3	1	468	Λαντάνα 2L	2L	15	4	\N	2025-05-22 07:20:18.369874	2025-05-22 07:21:13.334777	\N	f	19
4	3	1807	Κιτρομηλιά Σακούλι	Σακούλι	2	6	\N	2025-05-22 08:14:43.666357	2025-05-22 08:14:43.66636	\N	f	19
6	3	1728	Λεβαντούλα 2L	2L	5	2	\N	2025-05-22 17:31:40.278632	2025-05-22 17:31:40.278636	\N	f	19
7	5	534	Στρελίτσια Nicolai 10L	10L	10	10	\N	2025-05-22 17:40:26.331399	2025-05-22 17:40:26.331403	\N	f	19
8	5	1965	Ευγενία Etna Fire	5L	5	26	\N	2025-05-22 17:41:15.102898	2025-05-22 17:41:15.102902	\N	f	19
9	6	1303	Nektarinia Sakouli	Sakouli	2	5.5	\N	2025-05-23 15:28:33.245185	2025-05-23 15:28:33.24519	\N	f	19
10	7	1908	Λεμονιά Eureka		2	6	\N	2025-05-26 09:29:45.560604	2025-05-26 09:29:45.560609	\N	f	5
11	7	1754	Κυπαρισσι Ορθοκλωνο Τοτεμ 10L - 80cm	10L	3	5	\N	2025-05-26 09:30:42.887523	2025-05-26 09:30:42.887527	\N	f	19
12	8	465	Αροδάφνη Μινι 2L	2L	20	2.5	\N	2025-05-26 14:46:42.958851	2025-05-26 14:46:42.958857	\N	f	19
5	4	457	Μαργαρίτα Ασημόφυλλη 2L	2L	170	2.5	\N	2025-05-22 09:00:24.303385	2025-05-26 14:59:28.929689	\N	f	19
\.


--
-- Data for Name: price_list; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.price_list (id, customer_id, product_id, price, effective_date, expiry_date, created_at, updated_at, source_file) FROM stdin;
236	1	457	1.75	\N	\N	2025-04-01 15:44:38.785115	2025-04-01 15:44:38.785118	upload_11
237	1	458	2.5	\N	\N	2025-04-01 15:44:39.014605	2025-04-01 15:44:39.014608	upload_11
238	1	459	6	\N	\N	2025-04-01 15:44:39.238398	2025-04-01 15:44:39.238401	upload_11
239	1	460	13	\N	\N	2025-04-01 15:44:39.46463	2025-04-01 15:44:39.464633	upload_11
240	1	461	6	\N	\N	2025-04-01 15:44:39.69485	2025-04-01 15:44:39.694854	upload_11
241	1	462	13	\N	\N	2025-04-01 15:44:39.923112	2025-04-01 15:44:39.923116	upload_11
242	1	463	2.5	\N	\N	2025-04-01 15:44:40.145512	2025-04-01 15:44:40.145516	upload_11
243	1	464	2.5	\N	\N	2025-04-01 15:44:40.372217	2025-04-01 15:44:40.37222	upload_11
245	1	466	3.5	\N	\N	2025-04-01 15:44:40.816741	2025-04-01 15:44:40.816744	upload_11
246	1	467	2.5	\N	\N	2025-04-01 15:44:41.037938	2025-04-01 15:44:41.037958	upload_11
247	1	468	2.5	\N	\N	2025-04-01 15:44:41.260054	2025-04-01 15:44:41.260058	upload_11
248	1	469	2.5	\N	\N	2025-04-01 15:44:41.481987	2025-04-01 15:44:41.481991	upload_11
249	1	470	2.5	\N	\N	2025-04-01 15:44:41.70463	2025-04-01 15:44:41.704633	upload_11
250	1	471	2.5	\N	\N	2025-04-01 15:44:41.962063	2025-04-01 15:44:41.962066	upload_11
251	1	472	2.5	\N	\N	2025-04-01 15:44:42.183189	2025-04-01 15:44:42.183193	upload_11
252	1	473	2.5	\N	\N	2025-04-01 15:44:42.404688	2025-04-01 15:44:42.404691	upload_11
253	1	474	2.75	\N	\N	2025-04-01 15:44:42.625086	2025-04-01 15:44:42.625089	upload_11
254	1	475	2.75	\N	\N	2025-04-01 15:44:42.851218	2025-04-01 15:44:42.851222	upload_11
255	1	476	2.75	\N	\N	2025-04-01 15:44:43.07238	2025-04-01 15:44:43.072384	upload_11
256	1	477	35	\N	\N	2025-04-01 15:44:43.299491	2025-04-01 15:44:43.299494	upload_11
257	1	478	13	\N	\N	2025-04-01 15:44:43.521843	2025-04-01 15:44:43.521847	upload_11
258	1	479	25	\N	\N	2025-04-01 15:44:43.744641	2025-04-01 15:44:43.744645	upload_11
259	1	480	2.75	\N	\N	2025-04-01 15:44:43.96678	2025-04-01 15:44:43.966784	upload_11
260	1	481	2.75	\N	\N	2025-04-01 15:44:44.187528	2025-04-01 15:44:44.18753	upload_11
261	1	482	2.75	\N	\N	2025-04-01 15:44:44.412054	2025-04-01 15:44:44.412057	upload_11
262	1	483	3	\N	\N	2025-04-01 15:44:44.632612	2025-04-01 15:44:44.632619	upload_11
263	1	484	3	\N	\N	2025-04-01 15:44:44.85357	2025-04-01 15:44:44.853573	upload_11
264	1	485	3	\N	\N	2025-04-01 15:44:45.127651	2025-04-01 15:44:45.127654	upload_11
265	1	486	3	\N	\N	2025-04-01 15:44:45.351609	2025-04-01 15:44:45.351613	upload_11
266	1	487	3	\N	\N	2025-04-01 15:44:45.572796	2025-04-01 15:44:45.572799	upload_11
267	1	488	3	\N	\N	2025-04-01 15:44:45.794398	2025-04-01 15:44:45.794402	upload_11
268	1	489	3	\N	\N	2025-04-01 15:44:46.014759	2025-04-01 15:44:46.014762	upload_11
269	1	490	10	\N	\N	2025-04-01 15:44:46.235799	2025-04-01 15:44:46.235802	upload_11
270	1	491	3.5	\N	\N	2025-04-01 15:44:46.45615	2025-04-01 15:44:46.456154	upload_11
271	1	492	3	\N	\N	2025-04-01 15:44:46.676423	2025-04-01 15:44:46.676426	upload_11
272	1	493	5.5	\N	\N	2025-04-01 15:44:46.896535	2025-04-01 15:44:46.896539	upload_11
273	1	494	13	\N	\N	2025-04-01 15:44:47.117426	2025-04-01 15:44:47.117429	upload_11
274	1	495	3	\N	\N	2025-04-01 15:44:47.338859	2025-04-01 15:44:47.338863	upload_11
275	1	496	3	\N	\N	2025-04-01 15:44:47.559485	2025-04-01 15:44:47.559488	upload_11
276	1	497	3	\N	\N	2025-04-01 15:44:47.781562	2025-04-01 15:44:47.781565	upload_11
277	1	498	3	\N	\N	2025-04-01 15:44:48.008292	2025-04-01 15:44:48.008296	upload_11
278	1	499	3	\N	\N	2025-04-01 15:44:48.270058	2025-04-01 15:44:48.270061	upload_11
279	1	500	3	\N	\N	2025-04-01 15:44:48.490603	2025-04-01 15:44:48.490608	upload_11
280	1	501	3	\N	\N	2025-04-01 15:44:48.711804	2025-04-01 15:44:48.711808	upload_11
281	1	502	3	\N	\N	2025-04-01 15:44:48.933728	2025-04-01 15:44:48.933731	upload_11
282	1	503	3	\N	\N	2025-04-01 15:44:49.155348	2025-04-01 15:44:49.155351	upload_11
283	1	504	3.5	\N	\N	2025-04-01 15:44:49.375665	2025-04-01 15:44:49.375668	upload_11
284	1	505	3.5	\N	\N	2025-04-01 15:44:49.596942	2025-04-01 15:44:49.596945	upload_11
285	1	506	3.5	\N	\N	2025-04-01 15:44:49.818408	2025-04-01 15:44:49.818411	upload_11
286	1	507	3.5	\N	\N	2025-04-01 15:44:50.039689	2025-04-01 15:44:50.039693	upload_11
287	1	508	3.5	\N	\N	2025-04-01 15:44:50.260998	2025-04-01 15:44:50.261001	upload_11
288	1	509	3.5	\N	\N	2025-04-01 15:44:50.481596	2025-04-01 15:44:50.481599	upload_11
289	1	510	5.5	\N	\N	2025-04-01 15:44:50.70394	2025-04-01 15:44:50.703944	upload_11
290	1	511	13	\N	\N	2025-04-01 15:44:50.924511	2025-04-01 15:44:50.924514	upload_11
291	1	512	5.5	\N	\N	2025-04-01 15:44:51.144643	2025-04-01 15:44:51.144646	upload_11
292	1	513	13	\N	\N	2025-04-01 15:44:51.36461	2025-04-01 15:44:51.364619	upload_11
293	1	514	5.5	\N	\N	2025-04-01 15:44:51.584962	2025-04-01 15:44:51.584965	upload_11
294	1	515	13	\N	\N	2025-04-01 15:44:51.805308	2025-04-01 15:44:51.805312	upload_11
295	1	516	13	\N	\N	2025-04-01 15:44:52.026602	2025-04-01 15:44:52.026605	upload_11
296	1	517	3.5	\N	\N	2025-04-01 15:44:52.247138	2025-04-01 15:44:52.247141	upload_11
297	1	518	3.5	\N	\N	2025-04-01 15:44:52.468171	2025-04-01 15:44:52.468174	upload_11
298	1	519	3.5	\N	\N	2025-04-01 15:44:52.695165	2025-04-01 15:44:52.695169	upload_11
299	1	520	3.5	\N	\N	2025-04-01 15:44:52.915829	2025-04-01 15:44:52.915832	upload_11
300	1	521	4.5	\N	\N	2025-04-01 15:44:53.137099	2025-04-01 15:44:53.137102	upload_11
301	1	522	6	\N	\N	2025-04-01 15:44:53.357927	2025-04-01 15:44:53.35793	upload_11
302	1	523	6	\N	\N	2025-04-01 15:44:53.578652	2025-04-01 15:44:53.578654	upload_11
303	1	524	7	\N	\N	2025-04-01 15:44:53.799239	2025-04-01 15:44:53.799242	upload_11
304	1	525	7	\N	\N	2025-04-01 15:44:54.019535	2025-04-01 15:44:54.019537	upload_11
305	1	526	7	\N	\N	2025-04-01 15:44:54.241013	2025-04-01 15:44:54.241016	upload_11
306	1	527	7	\N	\N	2025-04-01 15:44:54.461147	2025-04-01 15:44:54.46115	upload_11
307	1	528	7	\N	\N	2025-04-01 15:44:54.682878	2025-04-01 15:44:54.682881	upload_11
308	1	529	8	\N	\N	2025-04-01 15:44:54.903315	2025-04-01 15:44:54.903318	upload_11
309	1	530	8	\N	\N	2025-04-01 15:44:55.124082	2025-04-01 15:44:55.124085	upload_11
310	1	531	8	\N	\N	2025-04-01 15:44:55.347285	2025-04-01 15:44:55.347288	upload_11
311	1	532	9	\N	\N	2025-04-01 15:44:55.569435	2025-04-01 15:44:55.569437	upload_11
312	1	533	10	\N	\N	2025-04-01 15:44:55.794538	2025-04-01 15:44:55.794541	upload_11
313	1	534	10	\N	\N	2025-04-01 15:44:56.016611	2025-04-01 15:44:56.016615	upload_11
314	1	535	10	\N	\N	2025-04-01 15:44:56.23897	2025-04-01 15:44:56.238973	upload_11
315	1	536	5.5	\N	\N	2025-04-01 15:44:56.462107	2025-04-01 15:44:56.46211	upload_11
316	1	537	13	\N	\N	2025-04-01 15:44:56.685501	2025-04-01 15:44:56.685505	upload_11
317	1	538	5.5	\N	\N	2025-04-01 15:44:56.907539	2025-04-01 15:44:56.907542	upload_11
318	1	539	13	\N	\N	2025-04-01 15:44:57.127992	2025-04-01 15:44:57.127995	upload_11
319	1	540	5.5	\N	\N	2025-04-01 15:44:57.348964	2025-04-01 15:44:57.348967	upload_11
320	1	541	13	\N	\N	2025-04-01 15:44:57.5695	2025-04-01 15:44:57.569504	upload_11
321	1	542	5.5	\N	\N	2025-04-01 15:44:57.7898	2025-04-01 15:44:57.789803	upload_11
322	1	543	13	\N	\N	2025-04-01 15:44:58.010608	2025-04-01 15:44:58.010611	upload_11
323	1	544	5.5	\N	\N	2025-04-01 15:44:58.231932	2025-04-01 15:44:58.231935	upload_11
324	1	545	13	\N	\N	2025-04-01 15:44:58.453117	2025-04-01 15:44:58.45312	upload_11
325	1	546	12	\N	\N	2025-04-01 15:44:58.674308	2025-04-01 15:44:58.674311	upload_11
326	1	530	15	\N	\N	2025-04-01 15:44:58.897614	2025-04-01 15:44:58.897617	upload_11
327	1	547	15	\N	\N	2025-04-01 15:44:59.118846	2025-04-01 15:44:59.118849	upload_11
328	1	548	15	\N	\N	2025-04-01 15:44:59.340613	2025-04-01 15:44:59.340617	upload_11
329	1	549	15	\N	\N	2025-04-01 15:44:59.562863	2025-04-01 15:44:59.562866	upload_11
330	1	550	20	\N	\N	2025-04-01 15:44:59.795665	2025-04-01 15:44:59.795669	upload_11
331	1	551	2	\N	\N	2025-04-01 15:45:00.018658	2025-04-01 15:45:00.018661	upload_11
332	1	552	3	\N	\N	2025-04-01 15:45:00.241266	2025-04-01 15:45:00.241269	upload_11
333	1	553	20	\N	\N	2025-04-01 15:45:00.462689	2025-04-01 15:45:00.462692	upload_11
334	1	554	25	\N	\N	2025-04-01 15:45:00.689136	2025-04-01 15:45:00.689139	upload_11
335	1	555	35	\N	\N	2025-04-01 15:45:00.910586	2025-04-01 15:45:00.910589	upload_11
336	1	556	35	\N	\N	2025-04-01 15:45:01.132268	2025-04-01 15:45:01.13227	upload_11
337	1	557	45	\N	\N	2025-04-01 15:45:01.352523	2025-04-01 15:45:01.352526	upload_11
338	1	558	50	\N	\N	2025-04-01 15:45:01.572811	2025-04-01 15:45:01.572814	upload_11
1320	2	466	2.5	\N	\N	2025-04-01 16:34:05.840818	2025-04-01 16:34:05.840822	upload_19
2070	2	519	3	\N	\N	2025-04-01 17:16:57.725583	2025-04-01 17:16:57.725586	upload_24
2071	2	1720	3.5	\N	\N	2025-04-01 17:16:57.943994	2025-04-01 17:16:57.943998	upload_24
2072	2	1721	3.5	\N	\N	2025-04-01 17:16:58.162569	2025-04-01 17:16:58.162572	upload_24
2073	2	1722	3.5	\N	\N	2025-04-01 17:16:58.381541	2025-04-01 17:16:58.381544	upload_24
2074	2	507	3.5	\N	\N	2025-04-01 17:16:58.527011	2025-04-01 17:16:58.527014	upload_24
2075	2	517	3.5	\N	\N	2025-04-01 17:16:58.672601	2025-04-01 17:16:58.672604	upload_24
2076	2	518	3.5	\N	\N	2025-04-01 17:16:58.818564	2025-04-01 17:16:58.818567	upload_24
2077	2	1723	4	\N	\N	2025-04-01 17:16:59.037028	2025-04-01 17:16:59.037031	upload_24
2078	2	528	5	\N	\N	2025-04-01 17:16:59.182835	2025-04-01 17:16:59.182838	upload_24
2079	2	1724	2	\N	\N	2025-04-01 17:16:59.400953	2025-04-01 17:16:59.400957	upload_24
2080	2	1725	2	\N	\N	2025-04-01 17:16:59.620508	2025-04-01 17:16:59.620511	upload_24
2081	2	1726	2	\N	\N	2025-04-01 17:16:59.839344	2025-04-01 17:16:59.839347	upload_24
2082	2	1727	2	\N	\N	2025-04-01 17:17:00.05714	2025-04-01 17:17:00.057143	upload_24
2083	2	1728	2	\N	\N	2025-04-01 17:17:00.275472	2025-04-01 17:17:00.275476	upload_24
2084	2	1729	2	\N	\N	2025-04-01 17:17:00.498996	2025-04-01 17:17:00.498999	upload_24
2085	2	471	2	\N	\N	2025-04-01 17:17:00.645115	2025-04-01 17:17:00.645117	upload_24
2086	2	469	2.5	\N	\N	2025-04-01 17:17:00.791991	2025-04-01 17:17:00.791994	upload_24
2087	2	470	2.5	\N	\N	2025-04-01 17:17:00.943041	2025-04-01 17:17:00.943045	upload_24
2088	2	492	2.5	\N	\N	2025-04-01 17:17:01.090133	2025-04-01 17:17:01.090137	upload_24
2089	2	495	2.5	\N	\N	2025-04-01 17:17:01.237625	2025-04-01 17:17:01.237629	upload_24
2090	2	499	2.5	\N	\N	2025-04-01 17:17:01.419355	2025-04-01 17:17:01.41936	upload_24
2091	2	1730	2.5	\N	\N	2025-04-01 17:17:01.648967	2025-04-01 17:17:01.648972	upload_24
2092	2	481	2.5	\N	\N	2025-04-01 17:17:01.794945	2025-04-01 17:17:01.794948	upload_24
2093	2	1731	2.75	\N	\N	2025-04-01 17:17:02.018999	2025-04-01 17:17:02.019003	upload_24
2094	2	486	3	\N	\N	2025-04-01 17:17:02.180007	2025-04-01 17:17:02.18001	upload_24
2095	2	500	3	\N	\N	2025-04-01 17:17:02.326409	2025-04-01 17:17:02.326412	upload_24
2096	2	1732	3	\N	\N	2025-04-01 17:17:02.552031	2025-04-01 17:17:02.552034	upload_24
2097	2	465	3.5	\N	\N	2025-04-01 17:17:02.698047	2025-04-01 17:17:02.69805	upload_24
2098	2	1733	4	\N	\N	2025-04-01 17:17:02.919854	2025-04-01 17:17:02.919858	upload_24
2099	2	527	6	\N	\N	2025-04-01 17:17:03.065676	2025-04-01 17:17:03.065678	upload_24
2100	2	468	2	\N	\N	2025-04-01 17:17:03.211708	2025-04-01 17:17:03.211711	upload_24
2101	2	483	2.5	\N	\N	2025-04-01 17:17:03.358236	2025-04-01 17:17:03.358239	upload_24
2102	2	484	2.5	\N	\N	2025-04-01 17:17:03.513866	2025-04-01 17:17:03.513869	upload_24
2103	2	458	2.5	\N	\N	2025-04-01 17:17:03.65995	2025-04-01 17:17:03.659953	upload_24
2104	2	463	2.5	\N	\N	2025-04-01 17:17:03.808272	2025-04-01 17:17:03.808275	upload_24
2105	2	1734	2.5	\N	\N	2025-04-01 17:17:04.026777	2025-04-01 17:17:04.02678	upload_24
2106	2	1735	2.5	\N	\N	2025-04-01 17:17:04.248094	2025-04-01 17:17:04.248097	upload_24
2107	2	488	2.5	\N	\N	2025-04-01 17:17:04.395985	2025-04-01 17:17:04.395987	upload_24
2108	2	487	2.5	\N	\N	2025-04-01 17:17:04.543201	2025-04-01 17:17:04.543204	upload_24
2109	2	489	2.5	\N	\N	2025-04-01 17:17:04.691031	2025-04-01 17:17:04.691034	upload_24
2110	2	480	2.5	\N	\N	2025-04-01 17:17:04.839556	2025-04-01 17:17:04.839559	upload_24
2111	2	497	2.5	\N	\N	2025-04-01 17:17:04.997044	2025-04-01 17:17:04.997047	upload_24
2112	2	1736	2.5	\N	\N	2025-04-01 17:17:05.218765	2025-04-01 17:17:05.218768	upload_24
2113	2	509	2.5	\N	\N	2025-04-01 17:17:05.365672	2025-04-01 17:17:05.365675	upload_24
2114	2	473	2.5	\N	\N	2025-04-01 17:17:05.512843	2025-04-01 17:17:05.512846	upload_24
2115	2	496	2.75	\N	\N	2025-04-01 17:17:05.659827	2025-04-01 17:17:05.659829	upload_24
2116	2	498	2.75	\N	\N	2025-04-01 17:17:05.806161	2025-04-01 17:17:05.806164	upload_24
2117	2	1737	3	\N	\N	2025-04-01 17:17:06.02488	2025-04-01 17:17:06.024884	upload_24
2118	2	1738	3.5	\N	\N	2025-04-01 17:17:06.245467	2025-04-01 17:17:06.24547	upload_24
2119	2	1739	3.5	\N	\N	2025-04-01 17:17:06.466632	2025-04-01 17:17:06.466636	upload_24
2120	2	522	6	\N	\N	2025-04-01 17:17:06.615941	2025-04-01 17:17:06.615944	upload_24
2121	2	523	6	\N	\N	2025-04-01 17:17:06.763648	2025-04-01 17:17:06.763651	upload_24
2122	2	1740	15	\N	\N	2025-04-01 17:17:07.015521	2025-04-01 17:17:07.015525	upload_24
2126	2	520	3.5	\N	\N	2025-04-01 17:17:07.829273	2025-04-01 17:17:07.829276	upload_24
2127	2	1744	4	\N	\N	2025-04-01 17:17:08.050544	2025-04-01 17:17:08.050547	upload_24
2128	2	1745	5	\N	\N	2025-04-01 17:17:08.268384	2025-04-01 17:17:08.268388	upload_24
2129	2	1746	5	\N	\N	2025-04-01 17:17:08.518319	2025-04-01 17:17:08.518323	upload_24
2124	2	1742	2.5	\N	\N	2025-04-01 17:17:07.457736	2025-04-08 13:20:42.040958	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2123	2	1741	2.5	\N	\N	2025-04-01 17:17:07.238192	2025-04-08 13:20:42.218686	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2069	2	1719	2.5	\N	\N	2025-04-01 17:16:57.571465	2025-04-08 13:35:49.93975	ffa30b9c-74e3-453e-b4e5-ec9cd7247872_1587.xlsx
2125	2	1743	2.75	\N	\N	2025-04-01 17:17:07.681562	2025-04-08 13:28:18.897845	b0ca6624-6140-4652-af99-b79acc2284ee_1167.xlsx
2130	2	549	10	\N	\N	2025-04-01 17:17:08.665559	2025-04-01 17:17:08.665562	upload_24
2131	2	466	2.5	\N	\N	2025-04-01 17:17:08.889062	2025-04-01 17:17:08.889068	upload_24
2132	2	552	3	\N	\N	2025-04-01 17:17:09.035328	2025-04-01 17:17:09.035331	upload_24
2133	2	1747	3	\N	\N	2025-04-01 17:17:09.253273	2025-04-01 17:17:09.253276	upload_24
2134	2	1748	3	\N	\N	2025-04-01 17:17:09.470313	2025-04-01 17:17:09.470316	upload_24
2135	2	491	3.5	\N	\N	2025-04-01 17:17:09.615318	2025-04-01 17:17:09.61532	upload_24
2136	2	1749	3.5	\N	\N	2025-04-01 17:17:09.877491	2025-04-01 17:17:09.877495	upload_24
2137	2	1750	3.5	\N	\N	2025-04-01 17:17:10.095337	2025-04-01 17:17:10.095341	upload_24
2138	2	1751	3.5	\N	\N	2025-04-01 17:17:10.31434	2025-04-01 17:17:10.314343	upload_24
2139	2	1752	3.5	\N	\N	2025-04-01 17:17:10.532975	2025-04-01 17:17:10.532978	upload_24
2140	2	1753	7	\N	\N	2025-04-01 17:17:10.750501	2025-04-01 17:17:10.750504	upload_24
2141	2	1754	13	\N	\N	2025-04-01 17:17:10.968672	2025-04-01 17:17:10.968675	upload_24
2142	2	1755	20	\N	\N	2025-04-01 17:17:11.192427	2025-04-01 17:17:11.192431	upload_24
2144	2	1757	3.5	\N	\N	2025-04-01 17:17:11.631706	2025-04-01 17:17:11.631708	upload_24
2145	2	524	6	\N	\N	2025-04-01 17:17:11.778237	2025-04-01 17:17:11.77824	upload_24
2146	2	1758	10	\N	\N	2025-04-01 17:17:11.997425	2025-04-01 17:17:11.997429	upload_24
2147	2	1759	15	\N	\N	2025-04-01 17:17:12.216395	2025-04-01 17:17:12.216399	upload_24
2148	2	1760	20	\N	\N	2025-04-01 17:17:12.438693	2025-04-01 17:17:12.438697	upload_24
2149	2	1761	50	\N	\N	2025-04-01 17:17:12.664242	2025-04-01 17:17:12.664246	upload_24
2150	3	457	1.75	\N	\N	2025-04-01 18:27:57.56588	2025-04-01 18:27:57.565883	upload_26
2151	3	1724	2	\N	\N	2025-04-01 18:27:57.721037	2025-04-01 18:27:57.72104	upload_26
2152	3	1725	2	\N	\N	2025-04-01 18:27:57.867296	2025-04-01 18:27:57.867299	upload_26
2153	3	1726	2	\N	\N	2025-04-01 18:27:58.013015	2025-04-01 18:27:58.013018	upload_26
2154	3	1727	2	\N	\N	2025-04-01 18:27:58.159418	2025-04-01 18:27:58.15942	upload_26
2155	3	1728	2	\N	\N	2025-04-01 18:27:58.304718	2025-04-01 18:27:58.30472	upload_26
2156	3	1763	2	\N	\N	2025-04-01 18:27:58.527646	2025-04-01 18:27:58.52765	upload_26
2157	3	1729	2	\N	\N	2025-04-01 18:27:58.678989	2025-04-01 18:27:58.678992	upload_26
2158	3	1735	2.5	\N	\N	2025-04-01 18:27:58.825019	2025-04-01 18:27:58.825022	upload_26
2159	3	468	2.5	\N	\N	2025-04-01 18:27:58.970959	2025-04-01 18:27:58.970962	upload_26
2160	3	469	2.5	\N	\N	2025-04-01 18:27:59.116368	2025-04-01 18:27:59.11637	upload_26
2161	3	470	2.5	\N	\N	2025-04-01 18:27:59.261715	2025-04-01 18:27:59.261718	upload_26
2162	3	519	2.5	\N	\N	2025-04-01 18:27:59.408086	2025-04-01 18:27:59.408088	upload_26
2163	3	471	2.5	\N	\N	2025-04-01 18:27:59.553364	2025-04-01 18:27:59.553366	upload_26
2164	3	472	2.5	\N	\N	2025-04-01 18:27:59.698534	2025-04-01 18:27:59.698537	upload_26
2165	3	473	2.5	\N	\N	2025-04-01 18:27:59.846079	2025-04-01 18:27:59.846082	upload_26
2166	3	483	2.75	\N	\N	2025-04-01 18:28:00.006426	2025-04-01 18:28:00.006428	upload_26
2167	3	484	2.75	\N	\N	2025-04-01 18:28:00.151485	2025-04-01 18:28:00.151487	upload_26
2168	3	464	2.75	\N	\N	2025-04-01 18:28:00.296769	2025-04-01 18:28:00.296772	upload_26
2169	3	465	2.75	\N	\N	2025-04-01 18:28:00.442332	2025-04-01 18:28:00.442334	upload_26
2170	3	1741	2.75	\N	\N	2025-04-01 18:28:00.587297	2025-04-01 18:28:00.587299	upload_26
2171	3	1734	2.75	\N	\N	2025-04-01 18:28:00.734012	2025-04-01 18:28:00.734015	upload_26
2173	3	474	2.75	\N	\N	2025-04-01 18:28:01.097225	2025-04-01 18:28:01.097229	upload_26
2174	3	532	2.75	\N	\N	2025-04-01 18:28:01.244193	2025-04-01 18:28:01.244196	upload_26
2175	3	1737	2.75	\N	\N	2025-04-01 18:28:01.393422	2025-04-01 18:28:01.393426	upload_26
2176	3	489	2.75	\N	\N	2025-04-01 18:28:01.540365	2025-04-01 18:28:01.540368	upload_26
2177	3	492	2.75	\N	\N	2025-04-01 18:28:01.685787	2025-04-01 18:28:01.68579	upload_26
2178	3	495	2.75	\N	\N	2025-04-01 18:28:01.830862	2025-04-01 18:28:01.830865	upload_26
2179	3	1743	2.75	\N	\N	2025-04-01 18:28:01.976105	2025-04-01 18:28:01.976108	upload_26
2180	3	496	2.75	\N	\N	2025-04-01 18:28:02.121263	2025-04-01 18:28:02.121265	upload_26
2181	3	509	2.75	\N	\N	2025-04-01 18:28:02.268393	2025-04-01 18:28:02.268395	upload_26
2182	3	499	2.75	\N	\N	2025-04-01 18:28:02.413949	2025-04-01 18:28:02.413951	upload_26
2183	3	500	2.75	\N	\N	2025-04-01 18:28:02.558907	2025-04-01 18:28:02.558911	upload_26
2184	3	501	2.75	\N	\N	2025-04-01 18:28:02.704536	2025-04-01 18:28:02.704537	upload_26
2185	3	1732	2.75	\N	\N	2025-04-01 18:28:02.849261	2025-04-01 18:28:02.849263	upload_26
2186	3	481	2.75	\N	\N	2025-04-01 18:28:02.994083	2025-04-01 18:28:02.994085	upload_26
2187	3	1765	2.75	\N	\N	2025-04-01 18:28:03.214639	2025-04-01 18:28:03.214642	upload_26
2188	3	1766	3	\N	\N	2025-04-01 18:28:03.431636	2025-04-01 18:28:03.431639	upload_26
2189	3	520	3	\N	\N	2025-04-01 18:28:03.57683	2025-04-01 18:28:03.576833	upload_26
2190	3	1767	3.5	\N	\N	2025-04-01 18:28:03.797391	2025-04-01 18:28:03.797395	upload_26
2191	3	1768	3.5	\N	\N	2025-04-01 18:28:04.014907	2025-04-01 18:28:04.01491	upload_26
2192	3	1742	3.5	\N	\N	2025-04-01 18:28:04.160479	2025-04-01 18:28:04.160482	upload_26
2193	3	1769	3.5	\N	\N	2025-04-01 18:28:04.378233	2025-04-01 18:28:04.378236	upload_26
2194	3	1736	3.5	\N	\N	2025-04-01 18:28:04.523448	2025-04-01 18:28:04.52345	upload_26
2195	3	1770	3.5	\N	\N	2025-04-01 18:28:04.74069	2025-04-01 18:28:04.740694	upload_26
2196	3	508	3.5	\N	\N	2025-04-01 18:28:04.885827	2025-04-01 18:28:04.885831	upload_26
2197	3	517	3.5	\N	\N	2025-04-01 18:28:05.030868	2025-04-01 18:28:05.03087	upload_26
2198	3	518	3.5	\N	\N	2025-04-01 18:28:05.176307	2025-04-01 18:28:05.176309	upload_26
2199	3	1771	5	\N	\N	2025-04-01 18:28:05.394457	2025-04-01 18:28:05.394461	upload_26
2200	3	523	6	\N	\N	2025-04-01 18:28:05.539451	2025-04-01 18:28:05.539453	upload_26
2201	3	506	10	\N	\N	2025-04-01 18:28:05.759535	2025-04-01 18:28:05.75954	upload_26
2202	3	534	10	\N	\N	2025-04-01 18:28:05.904942	2025-04-01 18:28:05.904945	upload_26
2203	3	1772	10	\N	\N	2025-04-01 18:28:06.122052	2025-04-01 18:28:06.122055	upload_26
2204	3	1773	10	\N	\N	2025-04-01 18:28:06.339072	2025-04-01 18:28:06.339076	upload_26
2205	4	551	1.25	\N	\N	2025-04-01 18:31:08.064058	2025-04-01 18:31:08.064061	upload_27
2206	4	1774	1.25	\N	\N	2025-04-01 18:31:08.300711	2025-04-01 18:31:08.300714	upload_27
2207	4	1775	1.25	\N	\N	2025-04-01 18:31:08.52619	2025-04-01 18:31:08.526194	upload_27
2208	4	1766	1.25	\N	\N	2025-04-01 18:31:08.676913	2025-04-01 18:31:08.676915	upload_27
2209	4	550	1.25	\N	\N	2025-04-01 18:31:08.82763	2025-04-01 18:31:08.827634	upload_27
2210	4	1724	1.25	\N	\N	2025-04-01 18:31:08.978167	2025-04-01 18:31:08.97817	upload_27
2211	4	1725	1.25	\N	\N	2025-04-01 18:31:09.12898	2025-04-01 18:31:09.128983	upload_27
2212	4	1726	1.25	\N	\N	2025-04-01 18:31:09.279663	2025-04-01 18:31:09.279665	upload_27
2213	4	1727	1.25	\N	\N	2025-04-01 18:31:09.430357	2025-04-01 18:31:09.43036	upload_27
2214	4	1728	1.25	\N	\N	2025-04-01 18:31:09.580347	2025-04-01 18:31:09.580349	upload_27
2215	4	1763	1.25	\N	\N	2025-04-01 18:31:09.730012	2025-04-01 18:31:09.730015	upload_27
2216	4	1776	1.25	\N	\N	2025-04-01 18:31:09.954261	2025-04-01 18:31:09.954265	upload_27
2217	4	1729	1.25	\N	\N	2025-04-01 18:31:10.104547	2025-04-01 18:31:10.10455	upload_27
2143	2	1756	3	\N	\N	2025-04-01 17:17:11.411245	2025-04-08 13:35:50.07063	ffa30b9c-74e3-453e-b4e5-ec9cd7247872_1587.xlsx
2218	4	1777	1.25	\N	\N	2025-04-01 18:31:10.329529	2025-04-01 18:31:10.329533	upload_27
2219	4	457	1.5	\N	\N	2025-04-01 18:31:10.480559	2025-04-01 18:31:10.480561	upload_27
2220	4	464	1.75	\N	\N	2025-04-01 18:31:10.632622	2025-04-01 18:31:10.632627	upload_27
2221	4	465	1.75	\N	\N	2025-04-01 18:31:10.782239	2025-04-01 18:31:10.782241	upload_27
2222	4	1778	1.75	\N	\N	2025-04-01 18:31:11.006877	2025-04-01 18:31:11.00688	upload_27
2223	4	471	1.75	\N	\N	2025-04-01 18:31:11.157266	2025-04-01 18:31:11.157269	upload_27
2224	4	473	2	\N	\N	2025-04-01 18:31:11.307394	2025-04-01 18:31:11.307397	upload_27
2225	4	474	2.25	\N	\N	2025-04-01 18:31:11.458398	2025-04-01 18:31:11.4584	upload_27
2226	4	552	2.25	\N	\N	2025-04-01 18:31:11.609115	2025-04-01 18:31:11.609117	upload_27
2227	4	1779	2.25	\N	\N	2025-04-01 18:31:11.833567	2025-04-01 18:31:11.83357	upload_27
2228	4	497	2.25	\N	\N	2025-04-01 18:31:11.983682	2025-04-01 18:31:11.983685	upload_27
2229	4	469	2.25	\N	\N	2025-04-01 18:31:12.133778	2025-04-01 18:31:12.133781	upload_27
2230	4	470	2.25	\N	\N	2025-04-01 18:31:12.284053	2025-04-01 18:31:12.284055	upload_27
2231	4	481	2.25	\N	\N	2025-04-01 18:31:12.434421	2025-04-01 18:31:12.434424	upload_27
2232	4	482	2.25	\N	\N	2025-04-01 18:31:12.591758	2025-04-01 18:31:12.59176	upload_27
2233	4	466	2.5	\N	\N	2025-04-01 18:31:12.741921	2025-04-01 18:31:12.741923	upload_27
2234	4	1742	2.5	\N	\N	2025-04-01 18:31:12.891948	2025-04-01 18:31:12.89195	upload_27
2235	4	1743	2.5	\N	\N	2025-04-01 18:31:13.042476	2025-04-01 18:31:13.042478	upload_27
2236	4	508	2.5	\N	\N	2025-04-01 18:31:13.193109	2025-04-01 18:31:13.193112	upload_27
2237	4	1749	2.5	\N	\N	2025-04-01 18:31:13.343188	2025-04-01 18:31:13.34319	upload_27
2238	4	1750	2.5	\N	\N	2025-04-01 18:31:13.49464	2025-04-01 18:31:13.494642	upload_27
2239	4	1751	2.5	\N	\N	2025-04-01 18:31:13.645637	2025-04-01 18:31:13.645639	upload_27
2240	4	1752	2.5	\N	\N	2025-04-01 18:31:13.795497	2025-04-01 18:31:13.795499	upload_27
2241	4	1748	2.5	\N	\N	2025-04-01 18:31:13.945268	2025-04-01 18:31:13.94527	upload_27
2242	4	1747	3	\N	\N	2025-04-01 18:31:14.095469	2025-04-01 18:31:14.095471	upload_27
2243	4	491	3.5	\N	\N	2025-04-01 18:31:14.24801	2025-04-01 18:31:14.248012	upload_27
2244	4	1780	5	\N	\N	2025-04-01 18:31:14.472771	2025-04-01 18:31:14.472774	upload_27
2245	4	529	8	\N	\N	2025-04-01 18:31:14.622226	2025-04-01 18:31:14.622229	upload_27
2246	5	1781	0.9	\N	\N	2025-04-01 18:35:38.471099	2025-04-01 18:35:38.471102	upload_28
2247	5	457	1.5	\N	\N	2025-04-01 18:35:38.627186	2025-04-01 18:35:38.627189	upload_28
2248	5	459	6	\N	\N	2025-04-01 18:35:38.779218	2025-04-01 18:35:38.77922	upload_28
2249	5	460	13	\N	\N	2025-04-01 18:35:38.930035	2025-04-01 18:35:38.930038	upload_28
2250	5	461	6	\N	\N	2025-04-01 18:35:39.081328	2025-04-01 18:35:39.08133	upload_28
2251	5	462	13	\N	\N	2025-04-01 18:35:39.231501	2025-04-01 18:35:39.231504	upload_28
2252	5	1735	1.75	\N	\N	2025-04-01 18:35:39.382123	2025-04-01 18:35:39.382126	upload_28
2253	5	1724	2	\N	\N	2025-04-01 18:35:39.533195	2025-04-01 18:35:39.533197	upload_28
2254	5	1725	2	\N	\N	2025-04-01 18:35:39.683406	2025-04-01 18:35:39.683408	upload_28
2255	5	466	3.5	\N	\N	2025-04-01 18:35:39.833606	2025-04-01 18:35:39.833608	upload_28
2256	5	1726	2	\N	\N	2025-04-01 18:35:39.984315	2025-04-01 18:35:39.984317	upload_28
2257	5	1727	2	\N	\N	2025-04-01 18:35:40.134739	2025-04-01 18:35:40.134741	upload_28
2258	5	1728	2	\N	\N	2025-04-01 18:35:40.291288	2025-04-01 18:35:40.29129	upload_28
2259	5	1729	2	\N	\N	2025-04-01 18:35:40.442855	2025-04-01 18:35:40.442858	upload_28
2260	5	1777	2	\N	\N	2025-04-01 18:35:40.593622	2025-04-01 18:35:40.593624	upload_28
2261	5	1719	2.5	\N	\N	2025-04-01 18:35:40.744399	2025-04-01 18:35:40.744401	upload_28
2262	5	458	2.5	\N	\N	2025-04-01 18:35:40.89488	2025-04-01 18:35:40.894882	upload_28
2263	5	463	2.5	\N	\N	2025-04-01 18:35:41.045369	2025-04-01 18:35:41.045371	upload_28
2264	5	1782	2.5	\N	\N	2025-04-01 18:35:41.270418	2025-04-01 18:35:41.270421	upload_28
2265	5	464	2.5	\N	\N	2025-04-01 18:35:41.420696	2025-04-01 18:35:41.420698	upload_28
2266	5	477	35	\N	\N	2025-04-01 18:35:41.571412	2025-04-01 18:35:41.571414	upload_28
2267	5	478	13	\N	\N	2025-04-01 18:35:41.72168	2025-04-01 18:35:41.721683	upload_28
2268	5	479	25	\N	\N	2025-04-01 18:35:41.872224	2025-04-01 18:35:41.872227	upload_28
2269	5	465	2.5	\N	\N	2025-04-01 18:35:42.022525	2025-04-01 18:35:42.022527	upload_28
2270	5	467	2.5	\N	\N	2025-04-01 18:35:42.172777	2025-04-01 18:35:42.17278	upload_28
2271	5	468	2.5	\N	\N	2025-04-01 18:35:42.323761	2025-04-01 18:35:42.323763	upload_28
2272	5	480	2.5	\N	\N	2025-04-01 18:35:42.473682	2025-04-01 18:35:42.473684	upload_28
2273	5	1736	2.5	\N	\N	2025-04-01 18:35:42.624526	2025-04-01 18:35:42.624529	upload_28
2274	5	469	2.5	\N	\N	2025-04-01 18:35:42.776514	2025-04-01 18:35:42.776517	upload_28
2275	5	470	2.5	\N	\N	2025-04-01 18:35:42.927106	2025-04-01 18:35:42.927108	upload_28
2276	5	471	2.5	\N	\N	2025-04-01 18:35:43.077745	2025-04-01 18:35:43.077748	upload_28
2277	5	472	2.5	\N	\N	2025-04-01 18:35:43.228595	2025-04-01 18:35:43.228598	upload_28
2278	5	473	2.5	\N	\N	2025-04-01 18:35:43.378847	2025-04-01 18:35:43.37885	upload_28
2279	5	490	10	\N	\N	2025-04-01 18:35:43.529409	2025-04-01 18:35:43.529412	upload_28
2280	5	491	3.5	\N	\N	2025-04-01 18:35:43.681215	2025-04-01 18:35:43.681218	upload_28
2281	5	1783	2.5	\N	\N	2025-04-01 18:35:43.906333	2025-04-01 18:35:43.906336	upload_28
2282	5	493	5.5	\N	\N	2025-04-01 18:35:44.056773	2025-04-01 18:35:44.056775	upload_28
2283	5	494	13	\N	\N	2025-04-01 18:35:44.207416	2025-04-01 18:35:44.207418	upload_28
2284	5	483	2.75	\N	\N	2025-04-01 18:35:44.357526	2025-04-01 18:35:44.357528	upload_28
2285	5	484	2.75	\N	\N	2025-04-01 18:35:44.507738	2025-04-01 18:35:44.507741	upload_28
2286	5	1734	2.75	\N	\N	2025-04-01 18:35:44.733165	2025-04-01 18:35:44.733167	upload_28
2288	5	474	2.75	\N	\N	2025-04-01 18:35:45.035779	2025-04-01 18:35:45.035781	upload_28
2289	5	1784	2.75	\N	\N	2025-04-01 18:35:45.262312	2025-04-01 18:35:45.262315	upload_28
2290	5	488	2.75	\N	\N	2025-04-01 18:35:45.414425	2025-04-01 18:35:45.414428	upload_28
2291	5	489	2.75	\N	\N	2025-04-01 18:35:45.565515	2025-04-01 18:35:45.565517	upload_28
2292	5	475	2.75	\N	\N	2025-04-01 18:35:45.715907	2025-04-01 18:35:45.715909	upload_28
2293	5	476	2.75	\N	\N	2025-04-01 18:35:45.866494	2025-04-01 18:35:45.866496	upload_28
2294	5	492	2.75	\N	\N	2025-04-01 18:35:46.017223	2025-04-01 18:35:46.017226	upload_28
2295	5	495	2.75	\N	\N	2025-04-01 18:35:46.168103	2025-04-01 18:35:46.168105	upload_28
2296	5	496	2.75	\N	\N	2025-04-01 18:35:46.318894	2025-04-01 18:35:46.318897	upload_28
2297	5	498	2.75	\N	\N	2025-04-01 18:35:46.469541	2025-04-01 18:35:46.469544	upload_28
2298	5	500	2.75	\N	\N	2025-04-01 18:35:46.620323	2025-04-01 18:35:46.620326	upload_28
2299	5	510	5.5	\N	\N	2025-04-01 18:35:46.770433	2025-04-01 18:35:46.770436	upload_28
2300	5	511	13	\N	\N	2025-04-01 18:35:46.922027	2025-04-01 18:35:46.922029	upload_28
2301	5	512	5.5	\N	\N	2025-04-01 18:35:47.072552	2025-04-01 18:35:47.072555	upload_28
2302	5	513	13	\N	\N	2025-04-01 18:35:47.2231	2025-04-01 18:35:47.223103	upload_28
2303	5	514	5.5	\N	\N	2025-04-01 18:35:47.373341	2025-04-01 18:35:47.373343	upload_28
2304	5	515	13	\N	\N	2025-04-01 18:35:47.524056	2025-04-01 18:35:47.524059	upload_28
2305	5	516	13	\N	\N	2025-04-01 18:35:47.674953	2025-04-01 18:35:47.674955	upload_28
2306	5	1731	2.75	\N	\N	2025-04-01 18:35:47.826018	2025-04-01 18:35:47.826021	upload_28
2307	5	481	2.75	\N	\N	2025-04-01 18:35:47.977265	2025-04-01 18:35:47.977268	upload_28
2308	5	1765	2.75	\N	\N	2025-04-01 18:35:48.140734	2025-04-01 18:35:48.140737	upload_28
2309	5	1737	3	\N	\N	2025-04-01 18:35:48.291811	2025-04-01 18:35:48.291815	upload_28
2310	5	486	3	\N	\N	2025-04-01 18:35:48.442422	2025-04-01 18:35:48.442425	upload_28
2311	5	497	3	\N	\N	2025-04-01 18:35:48.592832	2025-04-01 18:35:48.592834	upload_28
2312	5	499	3	\N	\N	2025-04-01 18:35:48.743315	2025-04-01 18:35:48.743317	upload_28
2313	5	1732	3	\N	\N	2025-04-01 18:35:48.893996	2025-04-01 18:35:48.893999	upload_28
2314	5	1730	3	\N	\N	2025-04-01 18:35:49.045382	2025-04-01 18:35:49.045385	upload_28
2315	5	1738	3	\N	\N	2025-04-01 18:35:49.196212	2025-04-01 18:35:49.196214	upload_28
2316	5	1733	3	\N	\N	2025-04-01 18:35:49.347396	2025-04-01 18:35:49.347399	upload_28
2317	5	1756	3.5	\N	\N	2025-04-01 18:35:49.50031	2025-04-01 18:35:49.500314	upload_28
2318	5	1720	3.5	\N	\N	2025-04-01 18:35:49.651452	2025-04-01 18:35:49.651461	upload_28
2319	5	1757	3.5	\N	\N	2025-04-01 18:35:49.806576	2025-04-01 18:35:49.806578	upload_28
2320	5	1741	3.5	\N	\N	2025-04-01 18:35:49.958981	2025-04-01 18:35:49.958984	upload_28
2321	5	1721	3.5	\N	\N	2025-04-01 18:35:50.115483	2025-04-01 18:35:50.115486	upload_28
2322	5	1722	3.5	\N	\N	2025-04-01 18:35:50.269291	2025-04-01 18:35:50.269294	upload_28
2323	5	1785	3.5	\N	\N	2025-04-01 18:35:50.494889	2025-04-01 18:35:50.494892	upload_28
2324	5	1742	3.5	\N	\N	2025-04-01 18:35:50.645286	2025-04-01 18:35:50.645288	upload_28
2325	5	487	3.5	\N	\N	2025-04-01 18:35:50.795722	2025-04-01 18:35:50.795725	upload_28
2326	5	536	5.5	\N	\N	2025-04-01 18:35:50.946901	2025-04-01 18:35:50.946904	upload_28
2327	5	537	13	\N	\N	2025-04-01 18:35:51.097188	2025-04-01 18:35:51.09719	upload_28
2328	5	538	5.5	\N	\N	2025-04-01 18:35:51.247786	2025-04-01 18:35:51.247789	upload_28
2329	5	539	13	\N	\N	2025-04-01 18:35:51.398644	2025-04-01 18:35:51.398647	upload_28
2330	5	540	5.5	\N	\N	2025-04-01 18:35:51.548932	2025-04-01 18:35:51.548934	upload_28
2331	5	541	13	\N	\N	2025-04-01 18:35:51.69928	2025-04-01 18:35:51.699282	upload_28
2332	5	542	5.5	\N	\N	2025-04-01 18:35:51.849923	2025-04-01 18:35:51.849925	upload_28
2333	5	543	13	\N	\N	2025-04-01 18:35:52.001124	2025-04-01 18:35:52.001127	upload_28
2334	5	544	5.5	\N	\N	2025-04-01 18:35:52.152353	2025-04-01 18:35:52.152356	upload_28
2335	5	545	13	\N	\N	2025-04-01 18:35:52.30276	2025-04-01 18:35:52.302762	upload_28
2336	5	504	3.5	\N	\N	2025-04-01 18:35:52.452827	2025-04-01 18:35:52.452829	upload_28
2337	5	505	3.5	\N	\N	2025-04-01 18:35:52.603201	2025-04-01 18:35:52.603203	upload_28
2338	5	1743	3.5	\N	\N	2025-04-01 18:35:52.75342	2025-04-01 18:35:52.753423	upload_28
2339	5	507	3.5	\N	\N	2025-04-01 18:35:52.903641	2025-04-01 18:35:52.903643	upload_28
2340	5	509	3.5	\N	\N	2025-04-01 18:35:53.054654	2025-04-01 18:35:53.054656	upload_28
2341	5	517	3.5	\N	\N	2025-04-01 18:35:53.204968	2025-04-01 18:35:53.20497	upload_28
2342	5	552	3	\N	\N	2025-04-01 18:35:53.356099	2025-04-01 18:35:53.356101	upload_28
2343	5	518	3.5	\N	\N	2025-04-01 18:35:53.509163	2025-04-01 18:35:53.509166	upload_28
2344	5	519	3.5	\N	\N	2025-04-01 18:35:53.659761	2025-04-01 18:35:53.659763	upload_28
2345	5	520	3.5	\N	\N	2025-04-01 18:35:53.810529	2025-04-01 18:35:53.810531	upload_28
2346	5	1786	3.5	\N	\N	2025-04-01 18:35:54.035265	2025-04-01 18:35:54.035268	upload_28
2347	5	1739	3.5	\N	\N	2025-04-01 18:35:54.188448	2025-04-01 18:35:54.18845	upload_28
2348	5	1723	4	\N	\N	2025-04-01 18:35:54.33978	2025-04-01 18:35:54.339782	upload_28
2349	5	1744	4	\N	\N	2025-04-01 18:35:54.490933	2025-04-01 18:35:54.490936	upload_28
2350	5	1745	5	\N	\N	2025-04-01 18:35:54.643219	2025-04-01 18:35:54.643222	upload_28
2351	5	1746	5	\N	\N	2025-04-01 18:35:54.810331	2025-04-01 18:35:54.810333	upload_28
2352	5	1787	8	\N	\N	2025-04-01 18:35:55.113046	2025-04-01 18:35:55.113049	upload_28
2353	5	1788	13	\N	\N	2025-04-01 18:35:55.338829	2025-04-01 18:35:55.338832	upload_28
2354	5	524	6	\N	\N	2025-04-01 18:35:55.490586	2025-04-01 18:35:55.490588	upload_28
2355	5	525	6	\N	\N	2025-04-01 18:35:55.641471	2025-04-01 18:35:55.641473	upload_28
2356	5	1789	6	\N	\N	2025-04-01 18:35:55.86723	2025-04-01 18:35:55.867234	upload_28
2357	5	1790	6	\N	\N	2025-04-01 18:35:56.093694	2025-04-01 18:35:56.093697	upload_28
2359	5	522	6	\N	\N	2025-04-01 18:35:56.46934	2025-04-01 18:35:56.469343	upload_28
2360	5	1792	5.5	\N	\N	2025-04-01 18:35:56.695334	2025-04-01 18:35:56.695338	upload_28
2361	5	1793	13	\N	\N	2025-04-01 18:35:56.921588	2025-04-01 18:35:56.921593	upload_28
2362	5	1794	5.5	\N	\N	2025-04-01 18:35:57.146648	2025-04-01 18:35:57.146652	upload_28
2363	5	1795	13	\N	\N	2025-04-01 18:35:57.374354	2025-04-01 18:35:57.374357	upload_28
2364	5	523	6	\N	\N	2025-04-01 18:35:57.52499	2025-04-01 18:35:57.524993	upload_28
2365	5	1796	6	\N	\N	2025-04-01 18:35:57.750337	2025-04-01 18:35:57.750341	upload_28
2366	5	1797	6	\N	\N	2025-04-01 18:35:57.975773	2025-04-01 18:35:57.975776	upload_28
2367	5	527	6	\N	\N	2025-04-01 18:35:58.127871	2025-04-01 18:35:58.127874	upload_28
2368	5	1798	6	\N	\N	2025-04-01 18:35:58.355483	2025-04-01 18:35:58.355486	upload_28
2369	5	1799	7	\N	\N	2025-04-01 18:35:58.581057	2025-04-01 18:35:58.58106	upload_28
2370	5	1753	7	\N	\N	2025-04-01 18:35:58.731706	2025-04-01 18:35:58.731708	upload_28
2371	5	1800	7	\N	\N	2025-04-01 18:35:58.957976	2025-04-01 18:35:58.957979	upload_28
2372	5	528	7	\N	\N	2025-04-01 18:35:59.109247	2025-04-01 18:35:59.10925	upload_28
2373	5	1801	8	\N	\N	2025-04-01 18:35:59.334602	2025-04-01 18:35:59.334606	upload_28
2374	5	1758	10	\N	\N	2025-04-01 18:35:59.490908	2025-04-01 18:35:59.490911	upload_28
2375	5	534	10	\N	\N	2025-04-01 18:35:59.64456	2025-04-01 18:35:59.644562	upload_28
2376	5	1802	7	\N	\N	2025-04-01 18:35:59.869979	2025-04-01 18:35:59.869982	upload_28
2377	5	1803	13	\N	\N	2025-04-01 18:36:00.106232	2025-04-01 18:36:00.106235	upload_28
2378	5	1804	13	\N	\N	2025-04-01 18:36:00.337814	2025-04-01 18:36:00.337818	upload_28
2379	5	1805	6	\N	\N	2025-04-01 18:36:00.565127	2025-04-01 18:36:00.56513	upload_28
2380	5	1806	13	\N	\N	2025-04-01 18:36:00.791576	2025-04-01 18:36:00.791579	upload_28
2381	5	549	10	\N	\N	2025-04-01 18:36:00.942576	2025-04-01 18:36:00.94258	upload_28
2382	5	1754	13	\N	\N	2025-04-01 18:36:01.09361	2025-04-01 18:36:01.093612	upload_28
2383	5	1759	15	\N	\N	2025-04-01 18:36:01.245684	2025-04-01 18:36:01.245686	upload_28
2384	5	1807	3.75	\N	\N	2025-04-01 18:36:01.473485	2025-04-01 18:36:01.473488	upload_28
2385	5	1808	13	\N	\N	2025-04-01 18:36:01.699601	2025-04-01 18:36:01.699604	upload_28
2386	5	1740	15	\N	\N	2025-04-01 18:36:01.851727	2025-04-01 18:36:01.85173	upload_28
2387	5	1809	15	\N	\N	2025-04-01 18:36:02.088889	2025-04-01 18:36:02.088893	upload_28
2388	5	1810	20	\N	\N	2025-04-01 18:36:02.314643	2025-04-01 18:36:02.314646	upload_28
2389	5	1811	9	\N	\N	2025-04-01 18:36:02.540129	2025-04-01 18:36:02.540132	upload_28
2390	5	1812	13	\N	\N	2025-04-01 18:36:02.766631	2025-04-01 18:36:02.766634	upload_28
2391	5	1813	5.5	\N	\N	2025-04-01 18:36:02.992892	2025-04-01 18:36:02.992896	upload_28
2392	5	1814	13	\N	\N	2025-04-01 18:36:03.219861	2025-04-01 18:36:03.219864	upload_28
2393	5	1760	20	\N	\N	2025-04-01 18:36:03.370923	2025-04-01 18:36:03.370925	upload_28
2394	5	1755	20	\N	\N	2025-04-01 18:36:03.521085	2025-04-01 18:36:03.521087	upload_28
2395	5	1815	25	\N	\N	2025-04-01 18:36:03.746042	2025-04-01 18:36:03.746046	upload_28
2396	5	1816	25	\N	\N	2025-04-01 18:36:03.970975	2025-04-01 18:36:03.970978	upload_28
2397	5	555	35	\N	\N	2025-04-01 18:36:04.209259	2025-04-01 18:36:04.209264	upload_28
2398	5	1761	50	\N	\N	2025-04-01 18:36:04.359546	2025-04-01 18:36:04.359548	upload_28
2399	6	487	3	2025-04-01	\N	2025-04-01 19:31:05.668038	2025-04-01 19:31:05.66804	Invoice #1551
2400	6	532	8	2025-04-01	\N	2025-04-01 19:31:06.257322	2025-04-01 19:31:06.257324	Invoice #1551
2401	6	1817	3	2025-04-01	\N	2025-04-01 19:31:07.361038	2025-04-01 19:31:07.361039	Invoice #1551
2402	6	1740	55	2025-04-01	\N	2025-04-01 19:31:07.943873	2025-04-01 19:31:07.943876	Invoice #1551
2403	7	487	3	2025-04-01	\N	2025-04-01 19:55:26.295499	2025-04-01 19:55:26.295503	Invoice #889
2404	7	1756	3.5	2025-04-01	\N	2025-04-01 19:55:26.704766	2025-04-01 19:55:26.704768	Invoice #889
2406	7	1819	35	2025-04-01	\N	2025-04-01 19:55:46.091983	2025-04-01 19:55:46.092013	Invoice #890
2408	7	1821	12	2025-04-01	\N	2025-04-01 19:55:47.423729	2025-04-01 19:55:47.423731	Invoice #890
2409	7	1822	15	2025-04-01	\N	2025-04-01 19:55:48.053743	2025-04-01 19:55:48.053746	Invoice #890
2410	7	530	15	2025-04-01	\N	2025-04-01 19:56:04.387904	2025-04-01 19:56:04.387908	Invoice #1112
2411	7	1823	75	2025-04-01	\N	2025-04-01 19:56:05.058592	2025-04-01 19:56:05.058595	Invoice #1112
2412	7	1801	8	2025-04-01	\N	2025-04-01 19:56:05.417641	2025-04-01 19:56:05.417644	Invoice #1112
2414	7	1825	2	2025-04-01	\N	2025-04-01 19:57:03.997239	2025-04-01 19:57:03.997242	Invoice #1302
2417	7	532	8	2025-04-01	\N	2025-04-01 19:57:05.681219	2025-04-01 19:57:05.681222	Invoice #1302
2418	7	474	3	2025-04-01	\N	2025-04-01 19:57:06.113231	2025-04-01 19:57:06.113233	Invoice #1302
2419	7	1828	5	2025-04-01	\N	2025-04-01 19:57:06.764673	2025-04-01 19:57:06.764676	Invoice #1302
2421	7	1830	15	2025-04-01	\N	2025-04-01 19:57:08.026047	2025-04-01 19:57:08.02605	Invoice #1302
2423	7	1817	3	2025-04-01	\N	2025-04-01 19:57:23.177057	2025-04-01 19:57:23.177059	Invoice #1381
2425	7	1832	7	2025-04-01	\N	2025-04-01 19:57:24.33361	2025-04-01 19:57:24.333613	Invoice #1381
2426	7	1266	4	2025-04-01	\N	2025-04-01 19:57:24.69232	2025-04-01 19:57:24.692323	Invoice #1381
2428	7	482	3.5	2025-04-01	\N	2025-04-01 19:57:44.746967	2025-04-01 19:57:44.746969	Invoice #1458
2429	7	458	3.5	2025-04-01	\N	2025-04-01 19:57:45.105695	2025-04-01 19:57:45.105698	Invoice #1458
2430	7	1834	3	2025-04-01	\N	2025-04-01 19:57:45.739363	2025-04-01 19:57:45.739365	Invoice #1458
2431	7	1835	20	2025-04-01	\N	2025-04-01 19:57:46.374348	2025-04-01 19:57:46.374351	Invoice #1458
2432	7	1732	3.5	2025-04-01	\N	2025-04-01 19:57:46.778853	2025-04-01 19:57:46.778856	Invoice #1458
2433	7	1836	5	2025-04-01	\N	2025-04-01 19:57:47.453679	2025-04-01 19:57:47.453681	Invoice #1458
2434	7	1837	10	2025-04-01	\N	2025-04-01 19:57:48.144678	2025-04-01 19:57:48.144681	Invoice #1458
2436	7	1839	30	2025-04-01	\N	2025-04-01 19:57:49.809744	2025-04-01 19:57:49.809747	Invoice #1458
2437	7	1840	10	2025-04-01	\N	2025-04-01 19:57:50.840702	2025-04-01 19:57:50.840704	Invoice #1458
2438	7	1841	40	2025-04-01	\N	2025-04-01 19:57:51.46745	2025-04-01 19:57:51.467453	Invoice #1458
2439	7	1842	10	2025-04-01	\N	2025-04-01 19:57:52.09098	2025-04-01 19:57:52.090984	Invoice #1458
2424	7	533	10	2025-04-01	\N	2025-04-01 19:57:23.704673	2025-04-01 19:58:24.090511	Invoice #1381
2442	4	1845	2.5	2025-04-02	\N	2025-04-02 11:30:12.093006	2025-04-02 11:30:12.093009	Invoice #1552
2443	4	1846	6	2025-04-02	\N	2025-04-02 11:30:12.748262	2025-04-02 11:30:12.748264	Invoice #1552
2444	8	1847	3	2025-04-02	\N	2025-04-02 12:25:48.964205	2025-04-02 12:25:48.964208	Invoice #1553
2475	10	1874	5.5	2025-04-04	\N	2025-04-04 14:54:40.460466	2025-04-04 14:54:40.460469	b4e773e8-11fa-4a11-a449-f2616206496b_Customer_Invoice_1566.xlsx
2498	10	1868	15	2025-04-04	\N	2025-04-04 15:17:43.371247	2025-04-04 15:17:43.371251	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2499	10	1869	3.5	2025-04-04	\N	2025-04-04 15:17:43.518072	2025-04-04 15:17:43.518074	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2500	10	472	2.5	2025-04-04	\N	2025-04-04 15:17:43.66225	2025-04-04 15:17:43.662253	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2501	10	1888	6	2025-04-04	\N	2025-04-04 15:17:43.805904	2025-04-04 15:17:43.805906	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2502	10	1871	5.5	2025-04-04	\N	2025-04-04 15:17:43.958844	2025-04-04 15:17:43.958846	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2503	10	1889	5.5	2025-04-04	\N	2025-04-04 15:17:44.102706	2025-04-04 15:17:44.102709	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2504	10	1873	3.5	2025-04-04	\N	2025-04-04 15:17:44.246237	2025-04-04 15:17:44.246239	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2505	10	1890	2.75	2025-04-04	\N	2025-04-04 15:17:44.390349	2025-04-04 15:17:44.390351	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2506	10	1891	6	2025-04-04	\N	2025-04-04 15:17:44.5344	2025-04-04 15:17:44.534402	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2507	10	1892	5.5	2025-04-04	\N	2025-04-04 15:17:44.749682	2025-04-04 15:17:44.749685	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2508	10	1893	5.5	2025-04-04	\N	2025-04-04 15:17:44.893152	2025-04-04 15:17:44.893154	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2509	10	1877	5.5	2025-04-04	\N	2025-04-04 15:17:45.036848	2025-04-04 15:17:45.036851	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2510	10	1858	3.5	2025-04-04	\N	2025-04-04 15:17:45.180192	2025-04-04 15:17:45.180194	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2511	10	1878	6	2025-04-04	\N	2025-04-04 15:17:45.324406	2025-04-04 15:17:45.324408	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2512	10	1879	6	2025-04-04	\N	2025-04-04 15:17:45.470994	2025-04-04 15:17:45.470997	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2513	10	1880	6	2025-04-04	\N	2025-04-04 15:17:45.616239	2025-04-04 15:17:45.616242	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2514	10	1894	6	2025-04-04	\N	2025-04-04 15:17:45.760496	2025-04-04 15:17:45.760499	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2515	10	1895	6	2025-04-04	\N	2025-04-04 15:17:45.905361	2025-04-04 15:17:45.905364	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2516	10	1883	6	2025-04-04	\N	2025-04-04 15:17:46.049928	2025-04-04 15:17:46.049931	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2517	10	1884	6	2025-04-04	\N	2025-04-04 15:17:46.195928	2025-04-04 15:17:46.19593	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2518	10	1885	15	2025-04-04	\N	2025-04-04 15:17:46.339643	2025-04-04 15:17:46.339646	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2519	10	1886	6	2025-04-04	\N	2025-04-04 15:17:46.484675	2025-04-04 15:17:46.484678	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2520	10	1887	5	2025-04-04	\N	2025-04-04 15:17:46.62854	2025-04-04 15:17:46.628543	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2521	10	498	2.75	2025-04-04	\N	2025-04-04 15:17:46.772748	2025-04-04 15:17:46.77275	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2522	10	1867	5	2025-04-04	\N	2025-04-04 15:17:46.916261	2025-04-04 15:17:46.916263	26f20646-3b67-47d0-bd46-20cb47915530_Customer_Invoice_1566.xlsx
2523	11	504	3.5	2025-04-04	\N	2025-04-04 15:26:58.45733	2025-04-04 15:26:58.457332	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2524	11	505	3.5	2025-04-04	\N	2025-04-04 15:26:58.551907	2025-04-04 15:26:58.551909	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2525	11	1742	3.5	2025-04-04	\N	2025-04-04 15:26:58.641264	2025-04-04 15:26:58.641266	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2526	11	1719	2.5	2025-04-04	\N	2025-04-04 15:26:58.731053	2025-04-04 15:26:58.73106	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2527	11	509	3	2025-04-04	\N	2025-04-04 15:26:58.821243	2025-04-04 15:26:58.821246	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2528	11	499	3	2025-04-04	\N	2025-04-04 15:26:58.91132	2025-04-04 15:26:58.911322	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2529	11	507	3.5	2025-04-04	\N	2025-04-04 15:26:59.001876	2025-04-04 15:26:59.001879	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2530	11	1799	8	2025-04-04	\N	2025-04-04 15:26:59.090973	2025-04-04 15:26:59.090975	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2531	11	1896	7	2025-04-04	\N	2025-04-04 15:26:59.181865	2025-04-04 15:26:59.181867	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2532	11	1734	3	2025-04-04	\N	2025-04-04 15:26:59.271164	2025-04-04 15:26:59.271166	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2533	11	1890	3	2025-04-04	\N	2025-04-04 15:26:59.360001	2025-04-04 15:26:59.360003	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2534	11	1897	3.5	2025-04-04	\N	2025-04-04 15:26:59.468854	2025-04-04 15:26:59.468856	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2535	11	1898	6	2025-04-04	\N	2025-04-04 15:26:59.557606	2025-04-04 15:26:59.557608	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2536	11	1899	2.5	2025-04-04	\N	2025-04-04 15:26:59.646547	2025-04-04 15:26:59.646549	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2537	11	1900	6	2025-04-04	\N	2025-04-04 15:26:59.735504	2025-04-04 15:26:59.735507	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2538	11	1901	12	2025-04-04	\N	2025-04-04 15:26:59.824838	2025-04-04 15:26:59.82484	243f35c9-7476-47e8-8846-fc951cfc53b2_1412.xlsx
2539	11	1902	3.5	2025-04-04	\N	2025-04-04 15:27:13.17575	2025-04-04 15:27:13.175752	0b06e6d2-2be5-4562-8472-59481050140a_1484.xlsx
2540	11	1903	3.5	2025-04-04	\N	2025-04-04 15:27:29.380397	2025-04-04 15:27:29.380399	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2541	11	1904	3.5	2025-04-04	\N	2025-04-04 15:27:29.469624	2025-04-04 15:27:29.469626	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2542	11	1905	3.5	2025-04-04	\N	2025-04-04 15:27:29.558574	2025-04-04 15:27:29.558576	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2543	11	1906	3.5	2025-04-04	\N	2025-04-04 15:27:29.647709	2025-04-04 15:27:29.647712	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2544	11	1880	6	2025-04-04	\N	2025-04-04 15:27:29.778549	2025-04-04 15:27:29.778551	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2545	11	1907	6	2025-04-04	\N	2025-04-04 15:27:29.869139	2025-04-04 15:27:29.869141	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2546	11	1908	6	2025-04-04	\N	2025-04-04 15:27:29.958685	2025-04-04 15:27:29.958687	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2547	11	1895	6	2025-04-04	\N	2025-04-04 15:27:30.047261	2025-04-04 15:27:30.047264	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2548	11	1909	9	2025-04-04	\N	2025-04-04 15:27:30.137003	2025-04-04 15:27:30.137005	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2549	11	1910	6	2025-04-04	\N	2025-04-04 15:27:30.225889	2025-04-04 15:27:30.225891	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2550	11	1911	6	2025-04-04	\N	2025-04-04 15:27:30.314928	2025-04-04 15:27:30.31493	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2551	11	1912	6	2025-04-04	\N	2025-04-04 15:27:30.404	2025-04-04 15:27:30.404003	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2552	11	1913	6	2025-04-04	\N	2025-04-04 15:27:30.493586	2025-04-04 15:27:30.493589	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2553	11	1914	6	2025-04-04	\N	2025-04-04 15:27:30.583071	2025-04-04 15:27:30.583073	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2554	11	1915	2.5	2025-04-04	\N	2025-04-04 15:27:30.673141	2025-04-04 15:27:30.673144	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2555	11	1877	6	2025-04-04	\N	2025-04-04 15:27:30.766654	2025-04-04 15:27:30.766655	d3687d0b-10be-4617-8932-cfcfa52b7d46_1512.xlsx
2556	11	1916	6	2025-04-04	\N	2025-04-04 15:27:45.924346	2025-04-04 15:27:45.924348	0069cd90-d750-4af2-84cf-47879d3ea177_1561.xlsx
2557	11	1917	2.5	2025-04-04	\N	2025-04-04 15:27:46.015583	2025-04-04 15:27:46.015585	0069cd90-d750-4af2-84cf-47879d3ea177_1561.xlsx
2558	11	498	3	2025-04-04	\N	2025-04-04 15:27:46.14896	2025-04-04 15:27:46.148962	0069cd90-d750-4af2-84cf-47879d3ea177_1561.xlsx
2559	11	1918	2.5	2025-04-04	\N	2025-04-04 15:27:46.239318	2025-04-04 15:27:46.239321	0069cd90-d750-4af2-84cf-47879d3ea177_1561.xlsx
2560	11	1919	3	2025-04-04	\N	2025-04-04 15:27:46.330919	2025-04-04 15:27:46.330922	0069cd90-d750-4af2-84cf-47879d3ea177_1561.xlsx
2561	11	1920	3	2025-04-04	\N	2025-04-04 15:27:46.41992	2025-04-04 15:27:46.419922	0069cd90-d750-4af2-84cf-47879d3ea177_1561.xlsx
2562	11	1921	2.5	2025-04-04	\N	2025-04-04 15:27:46.510387	2025-04-04 15:27:46.51039	0069cd90-d750-4af2-84cf-47879d3ea177_1561.xlsx
2563	12	1922	2	2025-04-04	\N	2025-04-04 15:32:16.149622	2025-04-04 15:32:16.149624	fb32ab15-00a9-4be6-a6dc-bb6fd965f8ae_1060.xlsx
2564	12	1763	2	2025-04-04	\N	2025-04-04 15:32:16.242927	2025-04-04 15:32:16.242929	fb32ab15-00a9-4be6-a6dc-bb6fd965f8ae_1060.xlsx
2565	12	1923	6	2025-04-04	\N	2025-04-04 15:32:16.331876	2025-04-04 15:32:16.331878	fb32ab15-00a9-4be6-a6dc-bb6fd965f8ae_1060.xlsx
2566	12	486	3	2025-04-04	\N	2025-04-04 15:32:16.420657	2025-04-04 15:32:16.420659	fb32ab15-00a9-4be6-a6dc-bb6fd965f8ae_1060.xlsx
2567	12	492	2.75	2025-04-04	\N	2025-04-04 15:32:16.511065	2025-04-04 15:32:16.511067	fb32ab15-00a9-4be6-a6dc-bb6fd965f8ae_1060.xlsx
2568	12	527	7	2025-04-04	\N	2025-04-04 15:32:16.599761	2025-04-04 15:32:16.599763	fb32ab15-00a9-4be6-a6dc-bb6fd965f8ae_1060.xlsx
2569	12	1924	7	2025-04-04	\N	2025-04-04 15:32:16.69134	2025-04-04 15:32:16.691342	fb32ab15-00a9-4be6-a6dc-bb6fd965f8ae_1060.xlsx
2570	12	1790	6	2025-04-04	\N	2025-04-04 15:32:38.956347	2025-04-04 15:32:38.956349	117dd488-815b-4304-be5d-4e276e2c4816_1146.xlsx
2571	12	1925	7	2025-04-04	\N	2025-04-04 15:32:39.045019	2025-04-04 15:32:39.045021	117dd488-815b-4304-be5d-4e276e2c4816_1146.xlsx
2572	12	470	2.5	2025-04-04	\N	2025-04-04 15:32:39.133753	2025-04-04 15:32:39.133756	117dd488-815b-4304-be5d-4e276e2c4816_1146.xlsx
2573	12	1926	2.5	2025-04-04	\N	2025-04-04 15:32:39.268729	2025-04-04 15:32:39.268731	117dd488-815b-4304-be5d-4e276e2c4816_1146.xlsx
2574	12	502	2.5	2025-04-04	\N	2025-04-04 15:32:39.359299	2025-04-04 15:32:39.359304	117dd488-815b-4304-be5d-4e276e2c4816_1146.xlsx
2575	12	1927	2.5	2025-04-04	\N	2025-04-04 15:32:39.448789	2025-04-04 15:32:39.448791	117dd488-815b-4304-be5d-4e276e2c4816_1146.xlsx
2576	12	1734	2.75	2025-04-04	\N	2025-04-04 15:34:33.936175	2025-04-04 15:34:33.936178	7e4a1cfd-6f76-40dd-a900-344a55e7b03d_1170.xlsx
2577	12	472	2.5	2025-04-04	\N	2025-04-04 15:34:34.029294	2025-04-04 15:34:34.029296	7e4a1cfd-6f76-40dd-a900-344a55e7b03d_1170.xlsx
2578	12	1928	6	2025-04-04	\N	2025-04-04 15:34:34.120685	2025-04-04 15:34:34.120687	7e4a1cfd-6f76-40dd-a900-344a55e7b03d_1170.xlsx
2579	12	1929	2.75	2025-04-04	\N	2025-04-04 15:34:34.208778	2025-04-04 15:34:34.20878	7e4a1cfd-6f76-40dd-a900-344a55e7b03d_1170.xlsx
2580	12	1930	2.75	2025-04-04	\N	2025-04-04 15:34:34.296994	2025-04-04 15:34:34.296996	7e4a1cfd-6f76-40dd-a900-344a55e7b03d_1170.xlsx
2581	12	1799	6	2025-04-04	\N	2025-04-04 15:34:34.384835	2025-04-04 15:34:34.384837	7e4a1cfd-6f76-40dd-a900-344a55e7b03d_1170.xlsx
2582	12	1931	2.5	2025-04-04	\N	2025-04-04 15:34:34.473057	2025-04-04 15:34:34.473059	7e4a1cfd-6f76-40dd-a900-344a55e7b03d_1170.xlsx
2583	12	1891	7	2025-04-04	\N	2025-04-04 15:34:57.016195	2025-04-04 15:34:57.016197	db71c0c2-fd92-4432-8b4e-5b3504e53474_1383.xlsx
2584	12	1742	3.5	2025-04-04	\N	2025-04-04 15:34:57.10523	2025-04-04 15:34:57.105232	db71c0c2-fd92-4432-8b4e-5b3504e53474_1383.xlsx
2585	12	499	2.75	2025-04-04	\N	2025-04-04 15:35:15.130761	2025-04-04 15:35:15.130764	c0469869-d918-41df-963a-224b79881c34_1417.xlsx
2586	13	1897	3.5	2025-04-06	\N	2025-04-06 12:55:44.86408	2025-04-06 12:55:44.864083	6240f66c-782e-4eb4-ac32-5bd76d662a7c_1570.xlsx
2587	13	1932	2.5	2025-04-06	\N	2025-04-06 12:55:44.956271	2025-04-06 12:55:44.956274	6240f66c-782e-4eb4-ac32-5bd76d662a7c_1570.xlsx
2588	13	1891	6	2025-04-06	\N	2025-04-06 12:55:45.044511	2025-04-06 12:55:45.044514	6240f66c-782e-4eb4-ac32-5bd76d662a7c_1570.xlsx
2589	12	1916	6	2025-04-06	\N	2025-04-06 13:01:50.904596	2025-04-06 13:01:50.904599	07037839-756c-42dd-8879-ddc02b832653_1571.xlsx
2590	12	1920	2.75	2025-04-06	\N	2025-04-06 13:01:51.024578	2025-04-06 13:01:51.024581	07037839-756c-42dd-8879-ddc02b832653_1571.xlsx
2591	12	1921	2.75	2025-04-06	\N	2025-04-06 13:01:51.113485	2025-04-06 13:01:51.113489	07037839-756c-42dd-8879-ddc02b832653_1571.xlsx
2592	12	465	2.5	2025-04-06	\N	2025-04-06 13:01:51.203098	2025-04-06 13:01:51.203101	07037839-756c-42dd-8879-ddc02b832653_1571.xlsx
2593	4	1933	1.25	2025-04-06	\N	2025-04-06 13:42:43.56778	2025-04-06 13:42:43.567785	337f3469-eaee-4b23-8175-c3c953fe434a_1572.xlsx
2594	4	1934	1.25	2025-04-06	\N	2025-04-06 13:42:43.706935	2025-04-06 13:42:43.706939	337f3469-eaee-4b23-8175-c3c953fe434a_1572.xlsx
2595	14	1935	15	2025-04-06	\N	2025-04-06 14:01:55.312973	2025-04-06 14:01:55.312976	c0e82fae-b09b-4e5f-b88b-da605a465e94_1575.xlsx
2596	14	1936	15	2025-04-06	\N	2025-04-06 14:01:55.402057	2025-04-06 14:01:55.40206	c0e82fae-b09b-4e5f-b88b-da605a465e94_1575.xlsx
2597	14	503	4	2025-04-06	\N	2025-04-06 14:01:55.487557	2025-04-06 14:01:55.48756	c0e82fae-b09b-4e5f-b88b-da605a465e94_1575.xlsx
2598	14	1937	3.5	2025-04-06	\N	2025-04-06 14:01:55.5725	2025-04-06 14:01:55.572503	c0e82fae-b09b-4e5f-b88b-da605a465e94_1575.xlsx
2599	2	1809	15	2025-04-06	\N	2025-04-06 14:17:39.875161	2025-04-06 14:17:39.875165	ea65bba0-1253-4dc1-904b-2d7e1df57114_1576.xlsx
2600	2	1867	5	2025-04-07	\N	2025-04-07 14:51:56.355552	2025-04-07 14:51:56.355554	cec9e1be-0647-4df3-b8be-fd568f57d926_1584.xlsx
2601	2	1920	2.5	2025-04-08	\N	2025-04-08 13:20:41.572093	2025-04-08 13:20:41.572096	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2602	2	1938	2.5	2025-04-08	\N	2025-04-08 13:20:41.685161	2025-04-08 13:20:41.685164	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2603	2	1939	3	2025-04-08	\N	2025-04-08 13:20:41.773917	2025-04-08 13:20:41.773919	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2604	2	1940	2	2025-04-08	\N	2025-04-08 13:20:41.864749	2025-04-08 13:20:41.864751	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2605	2	1917	2.5	2025-04-08	\N	2025-04-08 13:20:41.954562	2025-04-08 13:20:41.954564	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2606	2	1941	2.5	2025-04-08	\N	2025-04-08 13:20:42.13146	2025-04-08 13:20:42.131463	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2607	2	1942	6	2025-04-08	\N	2025-04-08 13:20:42.409562	2025-04-08 13:20:42.409564	40f8c04b-ae25-4392-9b3d-51e07ba94772_0001.xlsx
2608	2	1915	2.5	2025-04-08	\N	2025-04-08 13:27:57.380331	2025-04-08 13:27:57.380334	315ce537-8709-42dd-8377-0ceac3a3d9b9_1117.xlsx
2609	2	1932	2.5	2025-04-08	\N	2025-04-08 13:27:57.477343	2025-04-08 13:27:57.477346	315ce537-8709-42dd-8377-0ceac3a3d9b9_1117.xlsx
2610	2	1943	3	2025-04-08	\N	2025-04-08 13:27:57.568333	2025-04-08 13:27:57.568336	315ce537-8709-42dd-8377-0ceac3a3d9b9_1117.xlsx
2611	2	1944	2.5	2025-04-08	\N	2025-04-08 13:28:07.730446	2025-04-08 13:28:07.730449	eb267369-1f47-4072-bb64-2a85105a2ef4_1147.xlsx
2612	2	1945	2.5	2025-04-08	\N	2025-04-08 13:28:18.628915	2025-04-08 13:28:18.628917	b0ca6624-6140-4652-af99-b79acc2284ee_1167.xlsx
2613	2	1925	6	2025-04-08	\N	2025-04-08 13:28:18.717752	2025-04-08 13:28:18.717755	b0ca6624-6140-4652-af99-b79acc2284ee_1167.xlsx
2614	2	1946	2.5	2025-04-08	\N	2025-04-08 13:28:18.808689	2025-04-08 13:28:18.808691	b0ca6624-6140-4652-af99-b79acc2284ee_1167.xlsx
2615	2	1919	2.5	2025-04-08	\N	2025-04-08 13:28:28.636011	2025-04-08 13:28:28.636013	3d07d71c-e0e9-46c2-b13a-ea564e8aeccb_1271.xlsx
2616	2	1947	10	2025-04-08	\N	2025-04-08 13:28:38.954192	2025-04-08 13:28:38.954194	4ec5c4d7-41cc-49bf-ae7a-78e0a7cedbda_1289.xlsx
2672	34	1979	4	2025-04-29	\N	2025-04-29 12:55:21.262112	2025-04-29 12:55:21.262115	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2673	34	1926	3	2025-04-29	\N	2025-04-29 12:55:21.39368	2025-04-29 12:55:21.393682	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2617	2	1948	25	2025-04-08	\N	2025-04-08 13:28:39.052066	2025-04-08 13:28:48.951127	4c258f42-a844-454b-b83a-ef41f19f1c97_1289.xlsx
2618	2	1949	4	2025-04-08	\N	2025-04-08 13:28:58.788032	2025-04-08 13:28:58.788034	15452e48-0b85-4b95-88e2-7073ac357760_1310.xlsx
2619	2	1950	10	2025-04-08	\N	2025-04-08 13:29:26.591348	2025-04-08 13:29:26.59135	5f30719a-155d-4ea6-b491-f64a52bfccf0_1448.xlsx
2620	2	1951	25	2025-04-08	\N	2025-04-08 13:29:26.680332	2025-04-08 13:29:26.680334	5f30719a-155d-4ea6-b491-f64a52bfccf0_1448.xlsx
2621	2	1934	1.5	2025-04-08	\N	2025-04-08 13:35:49.851104	2025-04-08 13:35:49.851106	ffa30b9c-74e3-453e-b4e5-ec9cd7247872_1587.xlsx
2622	21	1891	10	2025-04-09	\N	2025-04-09 12:11:34.566578	2025-04-09 12:11:34.566581	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2623	21	1952	10	2025-04-09	\N	2025-04-09 12:11:34.664011	2025-04-09 12:11:34.664014	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2625	21	473	3	2025-04-09	\N	2025-04-09 12:11:34.83976	2025-04-09 12:11:34.839764	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2626	21	486	5	2025-04-09	\N	2025-04-09 12:11:34.92611	2025-04-09 12:11:34.926113	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2627	21	531	10	2025-04-09	\N	2025-04-09 12:11:35.012613	2025-04-09 12:11:35.012616	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2628	21	1916	8	2025-04-09	\N	2025-04-09 12:11:35.099048	2025-04-09 12:11:35.099051	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2629	21	1954	8	2025-04-09	\N	2025-04-09 12:11:35.185183	2025-04-09 12:11:35.185186	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2630	21	1928	10	2025-04-09	\N	2025-04-09 12:11:35.271109	2025-04-09 12:11:35.271111	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2631	21	1955	7	2025-04-09	\N	2025-04-09 12:11:35.356912	2025-04-09 12:11:35.356914	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2632	21	1956	4.5	2025-04-09	\N	2025-04-09 12:11:35.44285	2025-04-09 12:11:35.442852	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2633	21	1926	3.75	2025-04-09	\N	2025-04-09 12:11:35.529372	2025-04-09 12:11:35.529374	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2634	21	1932	3.5	2025-04-09	\N	2025-04-09 12:11:35.615538	2025-04-09 12:11:35.615541	e52e72e0-89f2-41f7-93fc-3efd067c366d_967.xlsx
2635	21	1897	4.5	2025-04-09	\N	2025-04-09 12:11:51.387723	2025-04-09 12:11:51.387727	ed83a415-c138-4bd8-bfd0-724649c9cbd9_1367.xlsx
2636	21	507	4.5	2025-04-09	\N	2025-04-09 12:11:51.475246	2025-04-09 12:11:51.475249	ed83a415-c138-4bd8-bfd0-724649c9cbd9_1367.xlsx
2624	21	1953	4.5	2025-04-09	\N	2025-04-09 12:11:34.751912	2025-04-09 12:11:51.603507	ed83a415-c138-4bd8-bfd0-724649c9cbd9_1367.xlsx
2637	21	1957	3.5	2025-04-09	\N	2025-04-09 12:11:51.691389	2025-04-09 12:11:51.691391	ed83a415-c138-4bd8-bfd0-724649c9cbd9_1367.xlsx
2638	21	1958	1.26	2025-04-09	\N	2025-04-09 12:12:08.470895	2025-04-09 12:12:08.470898	08dcd481-24a4-4e48-bbe9-dcbff7286a15_1370.xlsx
2639	10	1821	15	2025-04-11	\N	2025-04-11 15:51:47.611091	2025-04-11 15:51:47.611094	Invoice #1596
2640	10	1863	6	2025-04-11	\N	2025-04-11 15:51:47.98441	2025-04-11 15:51:47.984414	Invoice #1596
2641	10	1959	5.5	2025-04-11	\N	2025-04-11 15:51:49.548467	2025-04-11 15:51:49.548469	Invoice #1596
2642	10	1960	6	2025-04-11	\N	2025-04-11 15:51:50.132389	2025-04-11 15:51:50.132391	Invoice #1596
2643	10	1961	15	2025-04-11	\N	2025-04-11 15:51:50.752361	2025-04-11 15:51:50.752365	Invoice #1596
2644	10	1962	6	2025-04-11	\N	2025-04-11 15:51:51.388151	2025-04-11 15:51:51.388153	Invoice #1596
2645	10	1963	5.5	2025-04-11	\N	2025-04-11 15:51:51.973131	2025-04-11 15:51:51.973133	Invoice #1596
2646	10	1908	6	2025-04-11	\N	2025-04-11 15:51:52.333906	2025-04-11 15:51:52.333909	Invoice #1596
2647	10	1964	3	2025-04-11	\N	2025-04-11 15:51:52.924397	2025-04-11 15:51:52.9244	Invoice #1596
2648	10	1965	12	2025-04-11	\N	2025-04-11 15:51:53.511071	2025-04-11 15:51:53.511074	Invoice #1596
2649	10	1966	3.5	2025-04-11	\N	2025-04-11 15:51:54.092949	2025-04-11 15:51:54.092952	Invoice #1596
2650	10	1967	2.75	2025-04-11	\N	2025-04-11 15:51:54.67616	2025-04-11 15:51:54.676163	Invoice #1596
2651	4	1923	6	2025-04-14	\N	2025-04-14 16:26:11.335183	2025-04-14 16:26:11.335186	bf78bb58-0ee0-417e-8dd1-3b3b16ad5d7c_1604.xlsx
2652	4	1920	2.25	2025-04-14	\N	2025-04-14 16:26:11.480389	2025-04-14 16:26:11.480392	bf78bb58-0ee0-417e-8dd1-3b3b16ad5d7c_1604.xlsx
2653	5	1968	2.5	2025-04-17	\N	2025-04-17 16:39:38.576445	2025-04-17 16:39:38.576447	Invoice #1617
2654	5	1969	2	2025-04-17	\N	2025-04-17 16:39:42.754414	2025-04-17 16:39:42.754417	Invoice #1617
2655	5	1970	35	2025-04-17	\N	2025-04-17 16:39:46.766721	2025-04-17 16:39:46.766724	Invoice #1617
2656	5	1849	2.5	2025-04-17	\N	2025-04-17 16:39:48.650806	2025-04-17 16:39:48.650808	Invoice #1617
2657	5	1971	15	2025-04-17	\N	2025-04-17 16:39:51.714472	2025-04-17 16:39:51.714474	Invoice #1617
2658	5	1972	7	2025-04-17	\N	2025-04-17 16:39:54.750575	2025-04-17 16:39:54.750576	Invoice #1617
2659	5	1973	2.5	2025-04-17	\N	2025-04-17 16:39:57.788761	2025-04-17 16:39:57.788764	Invoice #1617
2662	34	473	2.5	2025-04-29	\N	2025-04-29 12:38:42.135276	2025-04-29 12:38:42.135279	3c9fc4e8-fa47-4aeb-b5ca-6dd20939d168_1507.xlsx
2663	34	1970	35	2025-04-29	\N	2025-04-29 12:38:42.227854	2025-04-29 12:38:42.227856	3c9fc4e8-fa47-4aeb-b5ca-6dd20939d168_1507.xlsx
2665	34	1932	2.75	2025-04-29	\N	2025-04-29 12:38:42.402498	2025-04-29 12:38:42.402501	3c9fc4e8-fa47-4aeb-b5ca-6dd20939d168_1507.xlsx
2666	34	1726	2	2025-04-29	\N	2025-04-29 12:38:42.491851	2025-04-29 12:38:42.491853	3c9fc4e8-fa47-4aeb-b5ca-6dd20939d168_1507.xlsx
2667	34	1978	30	2025-04-29	\N	2025-04-29 12:55:20.719482	2025-04-29 12:55:20.719485	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2664	34	1977	30	2025-04-29	\N	2025-04-29 12:38:42.314924	2025-04-29 12:55:20.809622	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2668	34	509	3.25	2025-04-29	\N	2025-04-29 12:55:20.899912	2025-04-29 12:55:20.899914	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2669	34	1724	2	2025-04-29	\N	2025-04-29 12:55:20.989274	2025-04-29 12:55:20.989276	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2670	34	1934	2	2025-04-29	\N	2025-04-29 12:55:21.076742	2025-04-29 12:55:21.076744	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2671	34	1933	2	2025-04-29	\N	2025-04-29 12:55:21.170204	2025-04-29 12:55:21.170207	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2674	34	1920	2.5	2025-04-29	\N	2025-04-29 12:55:21.480673	2025-04-29 12:55:21.480675	d89af6ba-7bcc-4cd3-a616-4573c43c9988_1648.xlsx
2676	37	1775	1.25	2025-05-22	\N	2025-05-22 07:01:14.64272	2025-05-22 07:01:14.642723	\N
2675	37	1834	3	2025-05-21	\N	2025-05-21 20:02:56.451205	2025-05-22 07:07:43.377422	\N
2677	37	468	4	2025-05-22	\N	2025-05-22 07:20:18.522533	2025-05-22 07:21:13.484526	\N
2678	1	1807	6	2025-05-22	\N	2025-05-22 08:14:43.820358	2025-05-22 08:14:43.820361	\N
2679	41	457	2.5	2025-05-22	\N	2025-05-22 09:00:24.477331	2025-05-22 09:00:24.477342	\N
2680	1	1728	2	2025-05-22	\N	2025-05-22 17:31:40.378784	2025-05-22 17:31:40.378788	\N
2681	42	534	10	2025-05-22	\N	2025-05-22 17:40:26.462964	2025-05-22 17:40:26.462968	\N
2682	42	1965	26	2025-05-22	\N	2025-05-22 17:41:15.192796	2025-05-22 17:41:15.1928	\N
2683	43	1303	5.5	2025-05-23	\N	2025-05-23 15:28:33.344899	2025-05-23 15:28:33.344904	\N
2684	44	1908	6	2025-05-26	\N	2025-05-26 09:29:45.661211	2025-05-26 09:29:45.661218	\N
2685	44	1754	5	2025-05-26	\N	2025-05-26 09:30:42.978703	2025-05-26 09:30:42.978707	\N
244	1	465	2.5	\N	\N	2025-04-01 15:44:40.594281	2025-05-26 14:46:43.062681	upload_11
2686	45	1927	2.5	2025-05-28	\N	2025-05-28 19:06:21.48019	2025-05-28 19:06:21.480193	manual_addition
2687	45	1756	3	2025-05-28	\N	2025-05-28 19:06:51.576276	2025-05-28 19:06:51.57628	manual_addition
2688	45	1919	2.5	2025-05-28	\N	2025-05-28 19:07:10.85635	2025-05-28 19:07:10.856352	manual_addition
2689	45	482	2.5	2025-05-28	\N	2025-05-28 19:07:36.899253	2025-05-28 19:07:36.899255	manual_addition
2690	45	480	2	2025-05-28	\N	2025-05-28 19:07:58.583793	2025-05-28 19:07:58.583796	manual_addition
2691	45	465	2	2025-05-28	\N	2025-05-28 19:08:27.429544	2025-05-28 19:08:27.429546	manual_addition
2692	45	457	1.75	2025-05-28	\N	2025-05-28 19:09:15.272101	2025-05-28 19:09:15.272103	manual_addition
2693	45	1726	1.5	2025-05-28	\N	2025-05-28 19:09:35.364829	2025-05-28 19:09:35.364832	manual_addition
2694	45	1777	2.5	2025-05-28	\N	2025-05-28 19:09:58.266688	2025-05-28 19:09:58.26669	manual_addition
2695	45	1897	2.5	2025-05-28	\N	2025-05-28 19:10:31.110284	2025-05-28 19:10:31.110287	manual_addition
2696	45	1734	2.5	2025-05-28	\N	2025-05-28 19:10:52.218525	2025-05-28 19:10:52.218527	manual_addition
2697	45	470	1.75	2025-05-28	\N	2025-05-28 19:12:05.690526	2025-05-28 19:12:05.690528	manual_addition
2698	45	469	1.75	2025-05-28	\N	2025-05-28 19:12:32.56525	2025-05-28 19:12:32.565252	manual_addition
2699	45	458	2.5	2025-05-28	\N	2025-05-28 19:12:52.540153	2025-05-28 19:12:52.540155	manual_addition
2700	45	1727	1.5	2025-05-28	\N	2025-05-28 19:13:16.992914	2025-05-28 19:13:16.992917	manual_addition
\.


--
-- Data for Name: price_list_item; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.price_list_item (id, price_list_id, product_id, name, size, price, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.product (id, name, sku, description, created_at, updated_at, category, scientific_name, pot) FROM stdin;
457	Μαργαρίτα Ασημόφυλλη 2L	\N	Gazania rigens 2L	2025-04-01 15:44:38.703731	2025-04-01 15:44:38.703735	Γρασίδια	Gazania rigens	2L
458	Αλτερναθέρα  2L	\N	Alternanthera dentata 2L	2025-04-01 15:44:38.940117	2025-04-01 15:44:38.94012	Θάμνοι	Alternanthera dentata	2L
459	Grapefruit Κόκκινο Σακούλι	\N	Σακούλι	2025-04-01 15:44:39.161618	2025-04-01 15:44:39.161622	Καρποφώρα	\N	Σακούλι
460	Grapefruit Κόκκινο Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:39.385947	2025-04-01 15:44:39.385951	Καρποφώρα	\N	Σακούλι 12L
461	Grapefruit Σακούλι	\N	Σακούλι	2025-04-01 15:44:39.613189	2025-04-01 15:44:39.613192	Καρποφώρα	\N	Σακούλι
462	Grapefruit Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:39.844833	2025-04-01 15:44:39.844836	Καρποφώρα	\N	Σακούλι 12L
463	Αλτερναθέρα Βραζιλιανα  2L	\N	Alternanthera Brasiliana 2L	2025-04-01 15:44:40.070585	2025-04-01 15:44:40.070588	Θάμνοι	Alternanthera Brasiliana	2L
464	Αροδάφνη Διπλή 2L	\N	Nerium oleander 2L	2025-04-01 15:44:40.292841	2025-04-01 15:44:40.292845	Θαμνοδεντρα	Nerium oleander	2L
465	Αροδάφνη Μινι 2L	\N	Nerium oleander 2L	2025-04-01 15:44:40.519537	2025-04-01 15:44:40.51954	Θαμνοδεντρα	Nerium oleander	2L
506	Κυπαρισσι Ορθοκλωνο Κίτρινο 5L	\N	Cupressus macrocarpa var. Aurea	2025-04-01 15:44:49.744105	2025-04-01 18:28:05.686126	Κωνοφόρα	Cupressus macrocarpa var. Aurea	2L
467	Ιβύσκος 2L	\N	Hibiscus 2L	2025-04-01 15:44:40.963477	2025-04-01 15:44:40.963481	Καλλωπιστικά Δέντρα	Hibiscus	2L
468	Λαντάνα 2L	\N	Lantana camara 2L	2025-04-01 15:44:41.18592	2025-04-01 15:44:41.185923	Θάμνοι	Lantana camara	2L
469	Πενισέτο Κόκκινο 2L	\N	Pennisetum Advena Rubrum 2L	2025-04-01 15:44:41.407335	2025-04-01 15:44:41.407343	Γρασίδια	Pennisetum Advena Rubrum	2L
470	Πενισέτο Πρασινο 2L	\N	Pennisetum Compr. White Flower 2L	2025-04-01 15:44:41.628999	2025-04-01 15:44:41.629003	Γρασίδια	Pennisetum Compr. White Flower	2L
471	Στίπα 2L	\N	Stipa 2L	2025-04-01 15:44:41.887967	2025-04-01 15:44:41.88797	Γρασίδια	Stipa	2L
472	Σχοινια 2L	\N	Schinus 2L	2025-04-01 15:44:42.108938	2025-04-01 15:44:42.108942	Καλλωπιστικά Δέντρα	Schinus	2L
473	Τουρπάτσια 2L	\N	TULBACHIA VIOLACEA 2L	2025-04-01 15:44:42.329673	2025-04-01 15:44:42.329677	Θάμνοι	TULBACHIA VIOLACEA	2L
474	Διέτης 2L	\N	Dietes 2L	2025-04-01 15:44:42.551013	2025-04-01 15:44:42.551015	Γρασίδια	Dietes	2L
475	Κοράλι - άσπρο 2L	\N	Russelia equisetiformis 2L	2025-04-01 15:44:42.77719	2025-04-01 15:44:42.777194	Θάμνοι	Russelia equisetiformis	2L
476	Κοράλι 2L	\N	Russelia equisetiformis 2L	2025-04-01 15:44:42.998023	2025-04-01 15:44:42.998067	Θάμνοι	Russelia equisetiformis	2L
477	Αβοκάτο 35L	\N	Persea americana 35L	2025-04-01 15:44:43.218953	2025-04-01 15:44:43.218957	Καρποφώρα	Persea americana	35L
478	Αβοκάτο Σακούλι	\N	Σακούλι	2025-04-01 15:44:43.447023	2025-04-01 15:44:43.447049	Καρποφώρα	\N	Σακούλι
479	Αβοκάτο Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:43.668549	2025-04-01 15:44:43.668553	Καρποφώρα	\N	Σακούλι 12L
480	Λεμονιουμ 2L	\N	Limonium 2L	2025-04-01 15:44:43.892372	2025-04-01 15:44:43.892376	Θάμνοι	Limonium	2L
481	Τουράντα  2L	\N	Duranta 2L	2025-04-01 15:44:44.113174	2025-04-01 15:44:44.113177	Θαμνοδεντρα	Duranta	2L
482	Τουράντα Gold 2L	\N	Duranta erecta 2L	2025-04-01 15:44:44.334571	2025-04-01 15:44:44.334575	Θαμνοδεντρα	Duranta erecta	2L
483	Αλαίαγνος ή Ελαίαγνος 2L	\N	Elaeagnus Pungens 2L	2025-04-01 15:44:44.55834	2025-04-01 15:44:44.558343	Θάμνοι	Elaeagnus Pungens	2L
484	Αλαίαγνος ή Ελαίαγνος Πράσινος 2L	\N	Elaeagnus Ebbingei 2L	2025-04-01 15:44:44.779122	2025-04-01 15:44:44.779126	Θάμνοι	Elaeagnus Ebbingei	2L
485	Διέτης πλατή φύλλο 2L	\N	Dietes 2L	2025-04-01 15:44:45.052491	2025-04-01 15:44:45.052494	Γρασίδια	Dietes	2L
486	Ζαντόξυλο 2L	\N	Zantoxilum 2L	2025-04-01 15:44:45.276628	2025-04-01 15:44:45.276631	Θαμνοδεντρα	Zantoxilum	2L
487	Κάρισσα με αγκαθι βαριεκατα 2L	\N	Carissa macrocarpa 2L	2025-04-01 15:44:45.498507	2025-04-01 15:44:45.49851	Θάμνοι	Carissa macrocarpa	2L
488	Κάρισσα με αγκαθι 2L	\N	Carissa macrocarpa 2L	2025-04-01 15:44:45.719549	2025-04-01 15:44:45.719552	Θάμνοι	Carissa macrocarpa	2L
489	Κάρισσα νάνα  2L	\N	Carissa macrocarpa 'Nana' 2L	2025-04-01 15:44:45.940767	2025-04-01 15:44:45.94077	Θάμνοι	Carissa macrocarpa 'Nana'	2L
490	Αμπέλι 10L	\N	Vitis 10L	2025-04-01 15:44:46.161776	2025-04-01 15:44:46.16178	Καρποφώρα	Vitis	10L
491	Αμπέλι 2L	\N	Vitis 2L	2025-04-01 15:44:46.382117	2025-04-01 15:44:46.382121	Καρποφώρα	Vitis	2L
492	Λευκόφυλλο γκρίζο 2L	\N	Leucophyllum candidum silver cloud 2L	2025-04-01 15:44:46.602469	2025-04-01 15:44:46.602472	Θαμνοδεντρα	Leucophyllum candidum silver cloud	2L
493	Αμυγδαλια Σακούλι	\N	Σακούλι	2025-04-01 15:44:46.822766	2025-04-01 15:44:46.822769	Καρποφώρα	\N	Σακούλι
494	Αμυγδαλια Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:47.043478	2025-04-01 15:44:47.043481	Καρποφώρα	\N	Σακούλι 12L
495	Λευκόφυλλο Πράσινο 2L	\N	Leucophyllum frutescens 2L	2025-04-01 15:44:47.263655	2025-04-01 15:44:47.263659	Θαμνοδεντρα	Leucophyllum frutescens	2L
496	Μερσινιά 2L	\N	Myrtus communis 2L	2025-04-01 15:44:47.485495	2025-04-01 15:44:47.485499	Θάμνοι	Myrtus communis	2L
497	Μερσυνια Ψυντρόφυλλη 2L	\N	Myrtus communis microphylla nana 2L	2025-04-01 15:44:47.706209	2025-04-01 15:44:47.706212	Θάμνοι	Myrtus communis microphylla nana	2L
498	Μετροσίδηρος 2L	\N	Μetrosideros excelsus 2L	2025-04-01 15:44:47.928717	2025-04-01 15:44:47.928721	Θάμνοι	Μetrosideros excelsus	2L
499	Πιττόσπορο Ορθοκλαδο 2L	\N	Pittosporum tobira 2L	2025-04-01 15:44:48.194459	2025-04-01 15:44:48.194463	Θαμνοδεντρα	Pittosporum tobira	2L
500	Πολύκαλα 2L	\N	Polygala myrtifolia 2L	2025-04-01 15:44:48.416363	2025-04-01 15:44:48.416366	Θαμνοδεντρα	Polygala myrtifolia	2L
501	Ραφιολέπης	\N	Rhaphiolepis umbellata 2L	2025-04-01 15:44:48.6368	2025-04-01 15:44:48.636803	Θάμνοι	Rhaphiolepis umbellata	2L
502	Χαμαικυπάρισσος γκρίζος 2L	\N	Juniperus sp. 2L	2025-04-01 15:44:48.858475	2025-04-01 15:44:48.858479	Κωνοφόρα	Juniperus sp.	2L
503	Χαμαικυπάρισσος πρασινος 2L	\N	Chamaecyparis lawsoniana 2L	2025-04-01 15:44:49.080219	2025-04-01 15:44:49.080222	Κωνοφόρα	Chamaecyparis lawsoniana	2L
504	Κισσός 2L	\N	Hedera helix 2L	2025-04-01 15:44:49.301721	2025-04-01 15:44:49.301725	Αναρριχώμενα	Hedera helix	2L
505	Κισσός δίχρωμος 2L	\N	Hedera helix 2L	2025-04-01 15:44:49.522315	2025-04-01 15:44:49.522319	Αναρριχώμενα	Hedera helix	2L
507	Παντορέα 2L	\N	Pandorea jasminoides 2L	2025-04-01 15:44:49.965002	2025-04-01 15:44:49.965006	Αναρριχώμενα	Pandorea jasminoides	2L
508	Πευκος 2L	\N	Pinus 2L	2025-04-01 15:44:50.186759	2025-04-01 15:44:50.186762	Κωνοφόρα	Pinus	2L
509	Πιττόσπορο Νάνο 2L	\N	Pittosporum Tobira ‘Nanum’ 2L	2025-04-01 15:44:50.407684	2025-04-01 15:44:50.407688	Θάμνοι	Pittosporum Tobira ‘Nanum’	2L
510	Αχλαδιά Super Fine Σακούλι	\N	Σακούλι	2025-04-01 15:44:50.629824	2025-04-01 15:44:50.629827	Καρποφώρα	\N	Σακούλι
511	Αχλαδιά Super Fine Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:50.850607	2025-04-01 15:44:50.850611	Καρποφώρα	\N	Σακούλι 12L
512	Αχλαδιά Κονφερενς Σακούλι	\N	Σακούλι	2025-04-01 15:44:51.070679	2025-04-01 15:44:51.070682	Καρποφώρα	\N	Σακούλι
513	Αχλαδιά Κονφερενς Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:51.290683	2025-04-01 15:44:51.290686	Καρποφώρα	\N	Σακούλι 12L
514	Αχλαδιά Κόρσια Σακούλι	\N	Σακούλι	2025-04-01 15:44:51.510928	2025-04-01 15:44:51.510931	Καρποφώρα	\N	Σακούλι
515	Αχλαδιά Κόρσια Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:51.731289	2025-04-01 15:44:51.731292	Καρποφώρα	\N	Σακούλι 12L
516	Βελανιδια Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:51.952616	2025-04-01 15:44:51.95262	Καρποφώρα	\N	Σακούλι 12L
517	Πυράκανθος κόκκινο 2L	\N	Pyracantha coccinea, Crataegus pyracantha 2L	2025-04-01 15:44:52.173222	2025-04-01 15:44:52.173226	Αναρριχώμενα	Pyracantha coccinea, Crataegus pyracantha	2L
518	Πυράκανθος πορτοκαλί 2L	\N	Pyracantha coccinea, Crataegus pyracantha 2L	2025-04-01 15:44:52.393352	2025-04-01 15:44:52.393356	Αναρριχώμενα	Pyracantha coccinea, Crataegus pyracantha	2L
519	Ρυγχόσπερμο 2L	\N	Rhynchospermum 2L	2025-04-01 15:44:52.61507	2025-04-01 15:44:52.615073	Αναρριχώμενα	Rhynchospermum	2L
520	τζακαράντα 2L	\N	J. Mimosifolia 2L	2025-04-01 15:44:52.841723	2025-04-01 15:44:52.841726	Καλλωπιστικά Δέντρα	J. Mimosifolia	2L
521	ΤΖΑΤΡΟΦΑ 2L	\N	Jatropha sp 2L	2025-04-01 15:44:53.062652	2025-04-01 15:44:53.062656	Θαμνοδεντρα	Jatropha sp	2L
522	Κάρισσα με αγκαθι  5L	\N	Carissa macrocarpa 5L	2025-04-01 15:44:53.284018	2025-04-01 15:44:53.284022	Θάμνοι	Carissa macrocarpa	5L
523	Κάρισσα νάνα  5L	\N	Carissa macrocarpa 'Nana' 5L	2025-04-01 15:44:53.504833	2025-04-01 15:44:53.504836	Θάμνοι	Carissa macrocarpa 'Nana'	5L
524	Αγάπανθος 5L	\N	Agapanthus africanus 5L	2025-04-01 15:44:53.725167	2025-04-01 15:44:53.72517	Πολυετή ποώδη φυτά	Agapanthus africanus	5L
525	Αλαίαγνος ή Ελαίαγνος 5L	\N	Elaeagnus Pungens 5L	2025-04-01 15:44:53.945471	2025-04-01 15:44:53.945474	Θάμνοι	Elaeagnus Pungens	5L
526	Μερσηνια Αφρικάνα 2L	\N	Myrsine africana 2L	2025-04-01 15:44:54.167087	2025-04-01 15:44:54.16709	Θάμνοι	Myrsine africana	2L
527	Σιεφλέρα ακτινόφυλλη 5L	\N	Schefflera actinophylla 5L	2025-04-01 15:44:54.387262	2025-04-01 15:44:54.387266	Θαμνοδεντρα	Schefflera actinophylla	5L
528	Τριανταφυλια Αναρριχώμενη Παξιανη	\N	Rosa Banksiae 5L	2025-04-01 15:44:54.60776	2025-04-01 15:44:54.607764	Αναρριχώμενα	Rosa Banksiae	5L
529	Διανέλλα	\N	3L	2025-04-01 15:44:54.829467	2025-04-01 15:44:54.829471	Others	\N	3L
531	Συζύγιο 5L	\N	Syzygium 5L	2025-04-01 15:44:55.270196	2025-04-01 15:44:55.270199	Θάμνοι	Syzygium	5L
532	Ευγενία Έτνα 2L	\N	Eugenia uniflora etna fire 2L	2025-04-01 15:44:55.495353	2025-04-01 15:44:55.495357	Θάμνοι	Eugenia uniflora etna fire	2L
533	Ροπελινη A	\N	Phoenix roebelenii 2L	2025-04-01 15:44:55.716002	2025-04-01 15:44:55.716005	Φοινικοειδή	Phoenix roebelenii	2L
534	Στρελίτσια Nicolai 10L	\N	Strelitzia nicolai 10L	2025-04-01 15:44:55.94154	2025-04-01 15:44:55.941543	Πολυετή ποώδη φυτά	Strelitzia nicolai	10L
535	Στρελίτσια Reginae 5L διπλη	\N	Strelitzia reginae 5L	2025-04-01 15:44:56.164469	2025-04-01 15:44:56.164472	Πολυετή ποώδη φυτά	Strelitzia reginae	5L
536	Δαμασκηνιά Black Amber Σακούλι	\N	Σακούλι	2025-04-01 15:44:56.387688	2025-04-01 15:44:56.387692	Καρποφώρα	\N	Σακούλι
537	Δαμασκηνιά Black Amber Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:56.610701	2025-04-01 15:44:56.610704	Καρποφώρα	\N	Σακούλι 12L
538	Δαμασκηνιά Black Diamond Σακούλι	\N	Σακούλι	2025-04-01 15:44:56.832856	2025-04-01 15:44:56.83286	Καρποφώρα	\N	Σακούλι
539	Δαμασκηνιά Black Diamond Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:57.053939	2025-04-01 15:44:57.053942	Καρποφώρα	\N	Σακούλι 12L
540	Δαμασκηνιά Stanley Σακούλι	\N	Σακούλι	2025-04-01 15:44:57.274849	2025-04-01 15:44:57.274853	Καρποφώρα	\N	Σακούλι
541	Δαμασκηνιά Stanley Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:57.495431	2025-04-01 15:44:57.495434	Καρποφώρα	\N	Σακούλι 12L
542	Δαμασκηνιά Σακούλι	\N	Σακούλι	2025-04-01 15:44:57.715948	2025-04-01 15:44:57.71595	Καρποφώρα	\N	Σακούλι
543	Δαμασκηνιά Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:57.936204	2025-04-01 15:44:57.936208	Καρποφώρα	\N	Σακούλι 12L
544	Δασμασκινιά President Σακούλι	\N	Σακούλι	2025-04-01 15:44:58.15712	2025-04-01 15:44:58.157123	Καρποφώρα	\N	Σακούλι
545	Δασμασκινιά President Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 15:44:58.378584	2025-04-01 15:44:58.378588	Καρποφώρα	\N	Σακούλι 12L
546	Κυπαρίσσι Αριζόνικα	\N	Cupressus arizonica 5L	2025-04-01 15:44:58.600199	2025-04-01 15:44:58.600203	Κωνοφόρα	Cupressus arizonica	5L
530	Κυπαρισσι Ορθοκλωνο Τοτεμ 10L	\N	Cupressus sempervirens totem 10L	2025-04-01 15:44:55.05018	2025-04-01 15:44:58.822631	Κωνοφόρα	Cupressus sempervirens totem	10L
547	Κυπαρισσι Ορθοκλωνο Τοτεμ 10L 1.5M	\N	Cupressus sempervirens totem 10L	2025-04-01 15:44:59.044725	2025-04-01 15:44:59.044729	Κωνοφόρα	Cupressus sempervirens totem	10L
548	Λακεστροεμια	\N	Lagerstroemia indica 10L	2025-04-01 15:44:59.266188	2025-04-01 15:44:59.266191	Καλλωπιστικά Δέντρα	Lagerstroemia indica	10L
549	τζακαράντα 10L	\N	J. Mimosifolia 10L	2025-04-01 15:44:59.488297	2025-04-01 15:44:59.4883	Καλλωπιστικά Δέντρα	J. Mimosifolia	10L
550	Κοκκινόφυλλη	\N	Prunus cerasifera 10L	2025-04-01 15:44:59.719889	2025-04-01 15:44:59.719892	\N	Prunus cerasifera	10L
551	Δυοσμος 2L	\N	Mentha spicata 2L	2025-04-01 15:44:59.944327	2025-04-01 15:44:59.94433	Αρωματικά	Mentha spicata	2L
552	Ελια 2L	\N	Olea europaea 2L	2025-04-01 15:45:00.166746	2025-04-01 15:45:00.166749	Καρποφώρα	Olea europaea	2L
553	Ροπελινη B	\N	Phoenix roebelenii 15L	2025-04-01 15:45:00.388286	2025-04-01 15:45:00.38829	Φοινικοειδή	Phoenix roebelenii	15L
554	Ροπελινη C	\N	Phoenix roebelenii 20L	2025-04-01 15:45:00.614421	2025-04-01 15:45:00.614425	Φοινικοειδή	Phoenix roebelenii	20L
556	Ροπελινη D	\N	Phoenix roebelenii 35L	2025-04-01 15:45:01.05826	2025-04-01 15:45:01.058264	Φοινικοειδή	Phoenix roebelenii	35L
557	Ροπελινη Double	\N	Phoenix roebelenii 35L	2025-04-01 15:45:01.278846	2025-04-01 15:45:01.278849	Φοινικοειδή	Phoenix roebelenii	35L
555	Αρχοντοφοίνικας D	\N	Archontophoenix alexander 25L	2025-04-01 15:45:00.836112	2025-04-01 18:36:04.121764	Φοινικοειδή	Archontophoenix alexander	25L
558	Αρχοντοφοίνικας E	\N	Archontophoenix alexander L	2025-04-01 15:45:01.499432	2025-04-01 15:45:01.499435	Φοινικοειδή	Archontophoenix alexander	L
1230	Karissa me agkathi 2L	\N	Carissa macrocarpa 2L	2025-04-01 16:34:07.278058	2025-04-01 16:34:07.278062	Thamnoi	Carissa macrocarpa	2L
1231	Karissa me agkathi bariekata 2L	\N	Carissa macrocarpa 2L	2025-04-01 16:34:07.493096	2025-04-01 16:34:07.493099	Thamnoi	Carissa macrocarpa	2L
1232	Karissa nana  2L	\N	Carissa macrocarpa 'Nana' 2L	2025-04-01 16:34:07.708365	2025-04-01 16:34:07.708367	Thamnoi	Carissa macrocarpa 'Nana'	2L
1233	Lemonioum 2L	\N	Limonium 2L	2025-04-01 16:34:07.923552	2025-04-01 16:34:07.923555	Thamnoi	Limonium	2L
1234	Leukophullo gkrizo 2L	\N	Leucophyllum candidum silver cloud 2L	2025-04-01 16:34:08.139133	2025-04-01 16:34:08.139135	Thamnodentra	Leucophyllum candidum silver cloud	2L
1235	Leukophullo Prasino 2L	\N	Leucophyllum frutescens 2L	2025-04-01 16:34:08.353907	2025-04-01 16:34:08.35391	Thamnodentra	Leucophyllum frutescens	2L
1236	Mersunia Psuntrophulle 2L	\N	Myrtus communis microphylla nana 2L	2025-04-01 16:34:08.568895	2025-04-01 16:34:08.568898	Thamnoi	Myrtus communis microphylla nana	2L
1237	Mouragia 2L	\N	Murraya 2L	2025-04-01 16:34:08.817469	2025-04-01 16:34:08.817472	Thamnoi	Murraya	2L
1238	Peniseto Kokkino 2L	\N	Pennisetum Advena Rubrum 2L	2025-04-01 16:34:09.037087	2025-04-01 16:34:09.03709	Grasidia	Pennisetum Advena Rubrum	2L
1239	Peniseto Prasino 2L	\N	Pennisetum Compr. White Flower 2L	2025-04-01 16:34:09.310017	2025-04-01 16:34:09.31002	Grasidia	Pennisetum Compr. White Flower	2L
1240	Pittosporo Nano 2L	\N	Pittosporum Tobira 'Nanum' 2L	2025-04-01 16:34:09.526921	2025-04-01 16:34:09.526924	Thamnoi	Pittosporum Tobira 'Nanum'	2L
1241	Pittosporo Orthoklado 2L	\N	Pittosporum tobira 2L	2025-04-01 16:34:09.742102	2025-04-01 16:34:09.742105	Thamnodentra	Pittosporum tobira	2L
1242	Tekomaria Kitrine e Tekoma tou akroteriou 2L	\N	Tecoma capensis 2L	2025-04-01 16:34:09.957307	2025-04-01 16:34:09.957326	Thamnodentra	Tecoma capensis	2L
1243	Touranta  2L	\N	Duranta 2L	2025-04-01 16:34:10.172528	2025-04-01 16:34:10.172531	Thamnodentra	Duranta	2L
1244	Tourpatsia 2L	\N	TULBACHIA VIOLACEA 2L	2025-04-01 16:34:10.387458	2025-04-01 16:34:10.387461	Thamnoi	TULBACHIA VIOLACEA	2L
1245	Mersinia 2L	\N	Myrtus communis 2L	2025-04-01 16:34:10.602938	2025-04-01 16:34:10.602942	Thamnoi	Myrtus communis	2L
1246	Metrosideros 2L	\N	Metrosideros excelsus 2L	2025-04-01 16:34:10.818712	2025-04-01 16:34:10.81873	Thamnoi	Metrosideros excelsus	2L
1247	Tekomaria Portokali 2L	\N	Tecoma capensis 2L	2025-04-01 16:34:11.03516	2025-04-01 16:34:11.035163	Thamnodentra	Tecoma capensis	2L
1249	Elia 2L	\N	Olea europaea 2L	2025-04-01 16:34:11.467657	2025-04-01 16:34:11.46766	Karpophora	Olea europaea	2L
1250	Ekhioum 2L	\N	Echium candicans 2L	2025-04-01 16:34:11.683217	2025-04-01 16:34:11.683221	Thamnoi	Echium candicans	2L
1251	Zantoxulo 2L	\N	Zantoxilum 2L	2025-04-01 16:34:11.898972	2025-04-01 16:34:11.898975	Thamnodentra	Zantoxilum	2L
1252	Polukala 2L	\N	Polygala myrtifolia 2L	2025-04-01 16:34:12.114274	2025-04-01 16:34:12.114277	Thamnodentra	Polygala myrtifolia	2L
1253	Rodies 2L	\N	Punica granatum 2L	2025-04-01 16:34:12.330158	2025-04-01 16:34:12.330162	Karpophora	Punica granatum	2L
1254	Rugkhospermo 2L	\N	Rhynchospermum 2L	2025-04-01 16:34:12.545393	2025-04-01 16:34:12.545396	Anarrikhomena	Rhynchospermum	2L
1255	Siephlera  2L	\N	Schefflera 2L	2025-04-01 16:34:12.762278	2025-04-01 16:34:12.762281	Thamnodentra	Schefflera	2L
1256	Sukia 2L	\N	Ficus carica 2L	2025-04-01 16:34:12.978392	2025-04-01 16:34:12.978395	Karpophora	Ficus carica	2L
1257	Agapanthos 2L	\N	Agapanthus africanus 2L	2025-04-01 16:34:13.194131	2025-04-01 16:34:13.194135	Poluete poode phuta	Agapanthus africanus	2L
1259	Ampeli 2L	\N	Vitis 2L	2025-04-01 16:34:13.627008	2025-04-01 16:34:13.627012	Karpophora	Vitis	2L
1260	Arakhne 2L	\N	Asparagus setaceus 2L	2025-04-01 16:34:13.842173	2025-04-01 16:34:13.842177	Poluete poode phuta	Asparagus setaceus	2L
1261	Arodaphne Mini 2L	\N	Nerium oleander 2L	2025-04-01 16:34:14.05632	2025-04-01 16:34:14.056323	Thamnodentra	Nerium oleander	2L
1262	Artumatia 2L	\N	Schinus molle 2L	2025-04-01 16:34:14.271629	2025-04-01 16:34:14.271632	Kallopistika Dentra	Schinus molle	2L
1264	Giasemi Kitrino 2L	\N	Gelsemium sempervirens 2L	2025-04-01 16:34:14.703862	2025-04-01 16:34:14.703864	Anarrikhomena	Gelsemium sempervirens	2L
1265	Kallistemonas 2L	\N	Callistemon Sp 2L	2025-04-01 16:34:14.918759	2025-04-01 16:34:14.918761	Kallopistika Dentra	Callistemon Sp	2L
1266	Mastikhodentro 2L	\N	Schinus terebinthifolius 2L	2025-04-01 16:34:15.145041	2025-04-01 16:34:15.145045	Kallopistika Dentra	Schinus terebinthifolius	2L
1267	Pantorea 2L	\N	Pandorea jasminoides 2L	2025-04-01 16:34:15.362909	2025-04-01 16:34:15.362912	Anarrikhomena	Pandorea jasminoides	2L
1268	Purakanthos kokkino 2L	\N	Pyracantha coccinea, Crataegus pyracantha 2L	2025-04-01 16:34:15.578108	2025-04-01 16:34:15.578111	Anarrikhomena	Pyracantha coccinea, Crataegus pyracantha	2L
1269	Purakanthos portokali 2L	\N	Pyracantha coccinea, Crataegus pyracantha 2L	2025-04-01 16:34:15.793421	2025-04-01 16:34:15.793424	Anarrikhomena	Pyracantha coccinea, Crataegus pyracantha	2L
1270	Sukia - Bardiko Sakouli	\N	Ficus carica Sakouli	2025-04-01 16:34:16.008743	2025-04-01 16:34:16.008746	Karpophora	Ficus carica	Sakouli
1271	Sukia - Basiliko Sakouli	\N	Ficus carica Sakouli	2025-04-01 16:34:16.22504	2025-04-01 16:34:16.225043	Karpophora	Ficus carica	Sakouli
1272	Sukia - Napolitana Nekra Sakouli	\N	Ficus carica Sakouli	2025-04-01 16:34:16.440526	2025-04-01 16:34:16.44053	Karpophora	Ficus carica	Sakouli
1273	Sukia - Smurneiko Sakouli	\N	Ficus carica Sakouli	2025-04-01 16:34:16.656348	2025-04-01 16:34:16.656351	Karpophora	Ficus carica	Sakouli
1274	tzakaranta 2L	\N	J. Mimosifolia 2L	2025-04-01 16:34:16.872343	2025-04-01 16:34:16.872346	Kallopistika Dentra	J. Mimosifolia	2L
1275	Triantaphulia Agrou 2L	\N	Rosa damascena 2L	2025-04-01 16:34:17.087861	2025-04-01 16:34:17.087864	Thamnoi	Rosa damascena	2L
1276	Photinia Nana 2L	\N	Photinia fraseri Nana 2L	2025-04-01 16:34:17.3105	2025-04-01 16:34:17.310503	Thamnoi	Photinia fraseri Nana	2L
1277	Kitromelia Sakouli	\N	Sakouli	2025-04-01 16:34:17.532159	2025-04-01 16:34:17.532162	Karpophora	\N	Sakouli
1278	Giasemi Mpala 2L	\N	Jasminum multipartitun 2L	2025-04-01 16:34:17.746957	2025-04-01 16:34:17.74696	Anarrikhomena	Jasminum multipartitun	2L
1279	Paskhalia 2L	\N	Syringa vulgaris 2L	2025-04-01 16:34:17.963324	2025-04-01 16:34:17.963326	Kallopistika Dentra	Syringa vulgaris	2L
1280	Photinia 2L	\N	Photinia fraseri red robin 2L	2025-04-01 16:34:18.178563	2025-04-01 16:34:18.178565	Thamnodentra	Photinia fraseri red robin	2L
1281	Kharoupia Agria Sakouli	\N	Sakouli	2025-04-01 16:34:18.393226	2025-04-01 16:34:18.393246	Karpophora	\N	Sakouli
1282	Triantaphulia Anarrikhomene Paxiane	\N	Rosa Banksiae 5L	2025-04-01 16:34:18.612206	2025-04-01 16:34:18.612209	Anarrikhomena	Rosa Banksiae	5L
1283	PhIKOS Mauros 15L	\N	Ficus benjamina 15L	2025-04-01 16:34:18.831617	2025-04-01 16:34:18.83162	Kallopistika Dentra	Ficus benjamina	15L
1284	PhIKOS Mauros 5L	\N	Ficus benjamina 5L	2025-04-01 16:34:19.050094	2025-04-01 16:34:19.050097	Kallopistika Dentra	Ficus benjamina	5L
1285	Amugdalia Sakouli	\N	Sakouli	2025-04-01 16:34:19.265864	2025-04-01 16:34:19.265868	Karpophora	\N	Sakouli
1286	Akhladia Super Fine Sakouli	\N	Sakouli	2025-04-01 16:34:19.481952	2025-04-01 16:34:19.481955	Karpophora	\N	Sakouli
1287	Akhladia Konpherens Sakouli	\N	Sakouli	2025-04-01 16:34:19.696617	2025-04-01 16:34:19.696621	Karpophora	\N	Sakouli
1288	Akhladia Korsia Sakouli	\N	Sakouli	2025-04-01 16:34:19.911929	2025-04-01 16:34:19.911933	Karpophora	\N	Sakouli
1289	Damaskenia Black Amber Sakouli	\N	Sakouli	2025-04-01 16:34:20.127938	2025-04-01 16:34:20.127941	Karpophora	\N	Sakouli
1290	Damaskenia Black Diamond Sakouli	\N	Sakouli	2025-04-01 16:34:20.344001	2025-04-01 16:34:20.344004	Karpophora	\N	Sakouli
1291	Damaskenia Stanley Sakouli	\N	Sakouli	2025-04-01 16:34:20.559599	2025-04-01 16:34:20.559603	Karpophora	\N	Sakouli
1292	Damaskenia Sakouli	\N	Sakouli	2025-04-01 16:34:20.774596	2025-04-01 16:34:20.7746	Karpophora	\N	Sakouli
1293	Dasmaskinia President Sakouli	\N	Sakouli	2025-04-01 16:34:20.993014	2025-04-01 16:34:20.993017	Karpophora	\N	Sakouli
1294	Kabapha Aspre Sakouli	\N	Sakouli	2025-04-01 16:34:21.208123	2025-04-01 16:34:21.208126	Karpophora	\N	Sakouli
1295	Kabapha Kokkine Sakouli	\N	Sakouli	2025-04-01 16:34:21.462318	2025-04-01 16:34:21.462322	Karpophora	\N	Sakouli
1296	Kudonia Sakouli	\N	Sakouli	2025-04-01 16:34:21.676926	2025-04-01 16:34:21.676929	Karpophora	\N	Sakouli
1297	Melia California Sakouli	\N	Sakouli	2025-04-01 16:34:21.891824	2025-04-01 16:34:21.891828	Karpophora	\N	Sakouli
1298	Melia Golden Delicious Sakouli	\N	Sakouli	2025-04-01 16:34:22.106809	2025-04-01 16:34:22.106813	Karpophora	\N	Sakouli
1299	Melia Granny Smith Sakouli	\N	Sakouli	2025-04-01 16:34:22.322373	2025-04-01 16:34:22.322376	Karpophora	\N	Sakouli
1300	Melia Royal Gala Sakouli	\N	Sakouli	2025-04-01 16:34:22.537596	2025-04-01 16:34:22.537599	Karpophora	\N	Sakouli
1301	Melia Anna Sakouli	\N	Sakouli	2025-04-01 16:34:22.752441	2025-04-01 16:34:22.752443	Karpophora	\N	Sakouli
1302	Melia Kathesto Sakouli	\N	Sakouli	2025-04-01 16:34:22.967636	2025-04-01 16:34:22.967639	Karpophora	\N	Sakouli
1303	Nektarinia Sakouli	\N	Sakouli	2025-04-01 16:34:23.327876	2025-04-01 16:34:23.327879	Karpophora	\N	Sakouli
1304	Rodakinia Sakouli	\N	Sakouli	2025-04-01 16:34:23.543117	2025-04-01 16:34:23.54312	Karpophora	\N	Sakouli
1305	Phormoza Sakouli	\N	Sakouli	2025-04-01 16:34:23.758294	2025-04-01 16:34:23.758297	Karpophora	\N	Sakouli
1306	Khrusomelia Sakouli	\N	Sakouli	2025-04-01 16:34:23.973909	2025-04-01 16:34:23.973912	Karpophora	\N	Sakouli
1307	Grapefruit Kokkino Sakouli	\N	Sakouli	2025-04-01 16:34:24.189123	2025-04-01 16:34:24.189126	Karpophora	\N	Sakouli
1308	Grapefruit Sakouli	\N	Sakouli	2025-04-01 16:34:24.404762	2025-04-01 16:34:24.404765	Karpophora	\N	Sakouli
1309	Agapanthos 5L	\N	Agapanthus africanus 5L	2025-04-01 16:34:24.621045	2025-04-01 16:34:24.621048	Poluete poode phuta	Agapanthus africanus	5L
1310	Karissa me agkathi  5L	\N	Carissa macrocarpa 5L	2025-04-01 16:34:24.836658	2025-04-01 16:34:24.836661	Thamnoi	Carissa macrocarpa	5L
1311	Karissa nana  5L	\N	Carissa macrocarpa 'Nana' 5L	2025-04-01 16:34:25.051607	2025-04-01 16:34:25.05161	Thamnoi	Carissa macrocarpa 'Nana'	5L
1312	Kerasia Sakouli	\N	Sakouli	2025-04-01 16:34:25.267613	2025-04-01 16:34:25.267616	Karpophora	\N	Sakouli
1313	Laim Sakouli	\N	Sakouli	2025-04-01 16:34:25.482701	2025-04-01 16:34:25.482704	Karpophora	\N	Sakouli
1719	Blue bango -Μπλε γιασεμί 2L	\N	Plumbago auriculata 2L	2025-04-01 17:16:57.49262	2025-04-01 17:16:57.492623	Αναρριχώμενα	Plumbago auriculata	2L
1720	Αγιόκλημα 2L	\N	Lonicera etrusca 2L	2025-04-01 17:16:57.870438	2025-04-01 17:16:57.870442	Αναρριχώμενα	Lonicera etrusca	2L
1721	Γιασεμί Γαλλικό 2L	\N	Jasminum multipartitun 2L	2025-04-01 17:16:58.089529	2025-04-01 17:16:58.089532	Αναρριχώμενα	Jasminum multipartitun	2L
1722	Γιασεμί Κίτρινο 2L	\N	Gelsemium sempervirens 2L	2025-04-01 17:16:58.308818	2025-04-01 17:16:58.308822	Αναρριχώμενα	Gelsemium sempervirens	2L
1723	Γιασεμί Μπάλα 2L	\N	Jasminum multipartitun 2L	2025-04-01 17:16:58.963755	2025-04-01 17:16:58.963775	Αναρριχώμενα	Jasminum multipartitun	2L
1724	Λασμαρί Έρπον 2L	\N	ROSMARINUS PROSTRATUS 2L	2025-04-01 17:16:59.327769	2025-04-01 17:16:59.327773	Αρωματικά	ROSMARINUS PROSTRATUS	2L
1725	Λασμαρί Ορθόκλαδο 2L	\N	Rosmarinus officinalis 2L	2025-04-01 17:16:59.546883	2025-04-01 17:16:59.546886	Αρωματικά	Rosmarinus officinalis	2L
1726	Λασμοαρί foxtail 2L	\N	Rosmarinus Officinalis Prostratus 2L	2025-04-01 17:16:59.765918	2025-04-01 17:16:59.765922	Αρωματικά	Rosmarinus Officinalis Prostratus	2L
1727	Λεβάντα Κυπριακή 2L	\N	Lavandula angustifolia 2L	2025-04-01 17:16:59.98395	2025-04-01 17:16:59.983953	Αρωματικά	Lavandula angustifolia	2L
1728	Λεβαντούλα 2L	\N	Lavandula 2L	2025-04-01 17:17:00.201997	2025-04-01 17:17:00.202	Αρωματικά	Lavandula	2L
1729	Σπατζιά ή Φασκόμηλο 2L	\N	Salvia cypria 2L	2025-04-01 17:17:00.420781	2025-04-01 17:17:00.420785	Αρωματικά	Salvia cypria	2L
1730	Τεκομάρια Κίτρινη ή Τεκόμα του ακρωτηρίου 2L	\N	Tecoma capensis 2L	2025-04-01 17:17:01.575657	2025-04-01 17:17:01.57566	Θαμνοδεντρα	Tecoma capensis	2L
1731	Τεκομάρια Πορτοκαλί 2L	\N	Tecoma capensis 2L	2025-04-01 17:17:01.94202	2025-04-01 17:17:01.942024	Θαμνοδεντρα	Tecoma capensis	2L
1732	Σιεφλέρα  2L	\N	Schefflera 2L	2025-04-01 17:17:02.471527	2025-04-01 17:17:02.471531	Θαμνοδεντρα	Schefflera	2L
1733	Φωτίνια 2L	\N	Photinia fraseri red robin 2L	2025-04-01 17:17:02.846626	2025-04-01 17:17:02.846629	Θαμνοδεντρα	Photinia fraseri red robin	2L
1734	Βιβούρνο λουσίντουμ 2L	\N	Viburnum lucidum 2L	2025-04-01 17:17:03.952941	2025-04-01 17:17:03.952945	Θάμνοι	Viburnum lucidum	2L
1735	Γκάουρα 2L	\N	Gaura 2L	2025-04-01 17:17:04.172469	2025-04-01 17:17:04.172473	Θάμνοι	Gaura	2L
1736	Μουράγια 2L	\N	Murraya 2L	2025-04-01 17:17:05.144265	2025-04-01 17:17:05.144269	Θάμνοι	Murraya	2L
1737	Εχιουμ 2L	\N	Echium candicans 2L	2025-04-01 17:17:05.951216	2025-04-01 17:17:05.951221	Θάμνοι	Echium candicans	2L
1738	Τριανταφυλια Αγρού 2L	\N	Rosa damascena 2L	2025-04-01 17:17:06.170733	2025-04-01 17:17:06.170737	Θάμνοι	Rosa damascena	2L
1739	Φωτίνια Νάνα 2L	\N	Photinia fraseri Nana 2L	2025-04-01 17:17:06.391081	2025-04-01 17:17:06.391085	Θάμνοι	Photinia fraseri Nana	2L
1740	Νολίνα ή Ponytail palm 5L	\N	Beaucarnea recurvata 5L	2025-04-01 17:17:06.940116	2025-04-01 17:17:06.940119	Θάμνοι	Beaucarnea recurvata	5L
1741	Αρτυματια 2L	\N	Schinus molle 2L	2025-04-01 17:17:07.164721	2025-04-01 17:17:07.164724	Καλλωπιστικά Δέντρα	Schinus molle	2L
1742	Καλλιστήμονας 2L	\N	Callistemon Sp 2L	2025-04-01 17:17:07.383816	2025-04-01 17:17:07.38382	Καλλωπιστικά Δέντρα	Callistemon Sp	2L
1743	Μαστιχόδεντρο 2L	\N	Schinus terebinthifolius 2L	2025-04-01 17:17:07.604198	2025-04-01 17:17:07.604223	Καλλωπιστικά Δέντρα	Schinus terebinthifolius	2L
1744	Πασχαλιά 2L	\N	Syringa vulgaris 2L	2025-04-01 17:17:07.974883	2025-04-01 17:17:07.974887	Καλλωπιστικά Δέντρα	Syringa vulgaris	2L
1745	ΦΙΚΟΣ Μάυρος 15L	\N	Ficus benjamina 15L	2025-04-01 17:17:08.195256	2025-04-01 17:17:08.19526	Καλλωπιστικά Δέντρα	Ficus benjamina	15L
1746	ΦΙΚΟΣ Μάυρος 5L	\N	Ficus benjamina 5L	2025-04-01 17:17:08.444787	2025-04-01 17:17:08.444791	Καλλωπιστικά Δέντρα	Ficus benjamina	5L
466	Passion fruit 2L	\N	Passiflora edulis 2L	2025-04-01 15:44:40.742277	2025-04-01 17:17:08.813333	Καρποφώρα	Passiflora edulis	2L
1747	Ροδιες 2L	\N	Punica granatum 2L	2025-04-01 17:17:09.180055	2025-04-01 17:17:09.180059	Καρποφώρα	Punica granatum	2L
1748	Συκια 2L	\N	Ficus carica 2L	2025-04-01 17:17:09.397635	2025-04-01 17:17:09.397639	Καρποφώρα	Ficus carica	2L
1749	Συκιά - Βάρδικο Σακούλι	\N	Ficus carica Σακούλι	2025-04-01 17:17:09.761819	2025-04-01 17:17:09.761822	Καρποφώρα	Ficus carica	Σακούλι
1750	Συκιά - Βασιλικό Σακούλι	\N	Ficus carica Σακούλι	2025-04-01 17:17:10.022314	2025-04-01 17:17:10.022318	Καρποφώρα	Ficus carica	Σακούλι
1751	Συκιά - Ναπολιτάνα Νέκρα Σακούλι	\N	Ficus carica Σακούλι	2025-04-01 17:17:10.240784	2025-04-01 17:17:10.240788	Καρποφώρα	Ficus carica	Σακούλι
1752	Συκιά - Σμυρνέικο Σακούλι	\N	Ficus carica Σακούλι	2025-04-01 17:17:10.459869	2025-04-01 17:17:10.459872	Καρποφώρα	Ficus carica	Σακούλι
1753	Θουγια 5L	\N	Thuja 5L	2025-04-01 17:17:10.677571	2025-04-01 17:17:10.677575	Κωνοφόρα	Thuja	5L
1754	Κυπαρισσι Ορθοκλωνο Τοτεμ 10L - 80cm	\N	Cupressus sempervirens totem 10L	2025-04-01 17:17:10.89586	2025-04-01 17:17:10.895864	Κωνοφόρα	Cupressus sempervirens totem	10L
1755	Κυπαρισσι Ορθοκλωνο Τοτεμ 10L 2M	\N	Cupressus sempervirens totem 10L	2025-04-01 17:17:11.115582	2025-04-01 17:17:11.115586	Κωνοφόρα	Cupressus sempervirens totem	10L
1756	Αγάπανθος 2L	\N	Agapanthus africanus 2L	2025-04-01 17:17:11.33806	2025-04-01 17:17:11.338063	Πολυετή ποώδη φυτά	Agapanthus africanus	2L
1757	Αράχνη 2L	\N	Asparagus setaceus 2L	2025-04-01 17:17:11.557083	2025-04-01 17:17:11.557087	Πολυετή ποώδη φυτά	Asparagus setaceus	2L
1758	Ροπελινη 2L	\N	Phoenix roebelenii 2L	2025-04-01 17:17:11.923551	2025-04-01 17:17:11.923555	Φοινικοειδή	Phoenix roebelenii	2L
1759	Neodypsis 10L	\N	Neodypsis leptocheilos 10L	2025-04-01 17:17:12.143298	2025-04-01 17:17:12.143302	Φοινικοειδή	Neodypsis leptocheilos	10L
1760	Αρεκάστρουμ 10L	\N	Syagrus romanzoffiana, the queen palm 10L	2025-04-01 17:17:12.362575	2025-04-01 17:17:12.362578	Φοινικοειδή	Syagrus romanzoffiana, the queen palm	10L
1761	Αρεκάστρουμ 35L	\N	Syagrus romanzoffiana, the queen palm 35L	2025-04-01 17:17:12.592279	2025-04-01 17:17:12.592283	Φοινικοειδή	Syagrus romanzoffiana, the queen palm	35L
1762	Κάρισσα - Test Product	\N	Δοκιμή Επιστημονικού Ονόματος 2L - Δοκιμή	2025-04-01 17:19:12.274492	2025-04-01 17:19:12.274496	Τεστ/Test	Δοκιμή Επιστημονικού Ονόματος	2L - Δοκιμή
1763	Ρίγανη 2L	\N	Origanum 2L	2025-04-01 18:27:58.451143	2025-04-01 18:27:58.451147	Αρωματικά	Origanum	2L
1765	Τουράντα erecta 2L	\N	Duranta erecta 2L	2025-04-01 18:28:03.140438	2025-04-01 18:28:03.140441	Θαμνοδεντρα	Duranta erecta	2L
1766	Κιούλι 2L	\N	Pelargonium odoratissimum 2L	2025-04-01 18:28:03.35897	2025-04-01 18:28:03.358972	Αρωματικά	Pelargonium odoratissimum	2L
1767	Solano 2L	\N	Solanum 2L	2025-04-01 18:28:03.72443	2025-04-01 18:28:03.724434	Θαμνοδεντρα	Solanum	2L
1768	Westringia 2L	\N	Westringia fruticosa 2L	2025-04-01 18:28:03.942147	2025-04-01 18:28:03.94215	Θάμνοι	Westringia fruticosa	2L
1769	Κρεβύλια 2L	\N	2L	2025-04-01 18:28:04.30468	2025-04-01 18:28:04.304683	Θάμνοδεντρα	\N	2L
1770	Μποχίνια 2L	\N	Bauhinia 2L	2025-04-01 18:28:04.667981	2025-04-01 18:28:04.667985	Καλλωπιστικά Δέντρα	Bauhinia	2L
1771	Σιεφλέρα  5L	\N	Schefflera 5L	2025-04-01 18:28:05.320915	2025-04-01 18:28:05.320918	Θαμνοδεντρα	Schefflera	5L
1772	Συκας 5L	\N	Cycas 5L	2025-04-01 18:28:06.049094	2025-04-01 18:28:06.049097	Φοινικοειδή	Cycas	5L
1773	ΦΙΚΟΣ ΑΜΣΤΕΛ 5L	\N	Ficus maclellandii cv. Ficus `Amstel King` 5L	2025-04-01 18:28:06.266246	2025-04-01 18:28:06.26625	Καλλωπιστικά Δέντρα	Ficus maclellandii cv. Ficus `Amstel King`	5L
1774	Θυμάρι 2L	\N	Thymus capitatus 2L	2025-04-01 18:31:08.222326	2025-04-01 18:31:08.222329	Αρωματικά	Thymus capitatus	2L
1775	Καρυ  2L	\N	Helichrysum Italicum 2L	2025-04-01 18:31:08.450492	2025-04-01 18:31:08.450496	Αρωματικά	Helichrysum Italicum	2L
1776	Σαντολίνα 2L	\N	Santolina 2L	2025-04-01 18:31:09.878863	2025-04-01 18:31:09.878866	Αρωματικά	Santolina	2L
1777	Τεύκριο 2L	\N	Teucrium 2L	2025-04-01 18:31:10.253723	2025-04-01 18:31:10.253727	Αρωματικά	Teucrium	2L
1778	Βιολέτα	\N	2L	2025-04-01 18:31:10.931518	2025-04-01 18:31:10.931521	\N	\N	2L
1779	Ελια Μοραγιόλου 2L	\N	Olea europaea 2L	2025-04-01 18:31:11.758275	2025-04-01 18:31:11.758279	Καρποφώρα	Olea europaea	2L
1780	Διέτης 5L	\N	Dietes 5L	2025-04-01 18:31:14.39723	2025-04-01 18:31:14.397234	Γρασίδια	Dietes	5L
1781	ΚΑΛΛΙΤΡΙΔΑ Σακούλι	\N	TETRACLINIS ARTICULATA Σακούλι	2025-04-01 18:35:38.393033	2025-04-01 18:35:38.393036	Κωνοφόρα	TETRACLINIS ARTICULATA	Σακούλι
1782	Αλτερναθέρα ψιντροφυλλη  2L	\N	Alternanthera 2L	2025-04-01 18:35:41.195085	2025-04-01 18:35:41.195089	Θάμνοι	Alternanthera	2L
1783	Χαμέλια 2L	\N	Hamelia 2L	2025-04-01 18:35:43.830907	2025-04-01 18:35:43.83091	Θάμνοι	Hamelia	2L
1784	Ευώνυμο 2L	\N	Euonymus japonicus 2L	2025-04-01 18:35:45.186663	2025-04-01 18:35:45.186666	Θάμνοι	Euonymus japonicus	2L
1785	Γιασεμί Πολυανθές 2L	\N	2L	2025-04-01 18:35:50.419598	2025-04-01 18:35:50.419602	Αναρριχώμενα	\N	2L
1786	ΦΙΚΟΣ ΑΜΣΤΕΛ 2L	\N	Ficus maclellandii cv. Ficus `Amstel King` 2L	2025-04-01 18:35:53.959897	2025-04-01 18:35:53.959899	Καλλωπιστικά Δέντρα	Ficus maclellandii cv. Ficus `Amstel King`	2L
1787	Ζιζιφια Σακούλι	\N	Σακούλι	2025-04-01 18:35:55.037761	2025-04-01 18:35:55.037765	Καρποφώρα	\N	Σακούλι
1788	Ζιζιφια Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 18:35:55.263252	2025-04-01 18:35:55.263255	Καρποφώρα	\N	Σακούλι 12L
1789	Βιβούρνο λουσίντουμ 5L	\N	Viburnum lucidum 5L	2025-04-01 18:35:55.791596	2025-04-01 18:35:55.791598	Θάμνοι	Viburnum lucidum	5L
1790	Βιβούρνο Τίνους 5L	\N	Viburnum tinus 5L	2025-04-01 18:35:56.017433	2025-04-01 18:35:56.017436	Θάμνοι	Viburnum tinus	5L
1792	Καβάφα Άσπρη Σακούλι	\N	Σακούλι	2025-04-01 18:35:56.619488	2025-04-01 18:35:56.619492	Καρποφώρα	\N	Σακούλι
1793	Καβάφα Άσπρη Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 18:35:56.845098	2025-04-01 18:35:56.845102	Καρποφώρα	\N	Σακούλι 12L
1794	Καβάφα Κόκκινη Σακούλι	\N	Σακούλι	2025-04-01 18:35:57.070872	2025-04-01 18:35:57.070875	Καρποφώρα	\N	Σακούλι
1795	Καβάφα Κόκκινη Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 18:35:57.298752	2025-04-01 18:35:57.298755	Καρποφώρα	\N	Σακούλι 12L
1796	Λευλάντι 5L	\N	Cupressus × leylandii 5L	2025-04-01 18:35:57.674786	2025-04-01 18:35:57.67479	Κωνοφόρα	Cupressus × leylandii	5L
1797	Μερσυνια Ψυντρόφυλλη 5L	\N	Myrtus communis microphylla nana 5L	2025-04-01 18:35:57.900532	2025-04-01 18:35:57.900536	Θάμνοι	Myrtus communis microphylla nana	5L
1798	Στρελίτσια Nicolai 5L	\N	Strelitzia nicolai 5L	2025-04-01 18:35:58.279924	2025-04-01 18:35:58.279927	Πολυετή ποώδη φυτά	Strelitzia nicolai	5L
1799	GoldCrest 5L	\N	Cupressus macrocarpa 'Gold Crest' 5L	2025-04-01 18:35:58.505662	2025-04-01 18:35:58.505666	Κωνοφόρα	Cupressus macrocarpa 'Gold Crest'	5L
1800	Κεράκι	\N	2L	2025-04-01 18:35:58.881894	2025-04-01 18:35:58.881898	Αναρριχώμενα	\N	2L
1801	Ιβύσκος Τηλεανθέος  5L	\N	Hibiscus tiliaceus 5L	2025-04-01 18:35:59.258956	2025-04-01 18:35:59.25896	Καλλωπιστικά Δέντρα	Hibiscus tiliaceus	5L
1802	Καρυδιά Κυπριακή Σακούλι	\N	Σακούλι	2025-04-01 18:35:59.794473	2025-04-01 18:35:59.794477	Καρποφώρα	\N	Σακούλι
1803	Καρυδιά Μοχώκ Σακούλι	\N	Σακούλι	2025-04-01 18:36:00.023587	2025-04-01 18:36:00.02359	Καρποφώρα	\N	Σακούλι
1804	Καρυδιά Πεκάν Σακούλι	\N	Σακούλι	2025-04-01 18:36:00.261217	2025-04-01 18:36:00.26122	Καρποφώρα	\N	Σακούλι
1805	Κερασιά Σακούλι	\N	Σακούλι	2025-04-01 18:36:00.48885	2025-04-01 18:36:00.488854	Καρποφώρα	\N	Σακούλι
1806	Κερασιά Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 18:36:00.715783	2025-04-01 18:36:00.715786	Καρποφώρα	\N	Σακούλι 12L
1807	Κιτρομηλιά Σακούλι	\N	Σακούλι	2025-04-01 18:36:01.396523	2025-04-01 18:36:01.396527	Καρποφώρα	\N	Σακούλι
1808	Κιτρομηλιά Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 18:36:01.623718	2025-04-01 18:36:01.623722	Καρποφώρα	\N	Σακούλι 12L
1809	Χαμαίρωπας Humilis 10L	\N	Chamaerops Humilis 10L	2025-04-01 18:36:02.012558	2025-04-01 18:36:02.012561	Φοινικοειδή	Chamaerops Humilis	10L
1810	Washingtonia 10L	\N	Washingtonian 10L	2025-04-01 18:36:02.238835	2025-04-01 18:36:02.238839	Φοινικοειδή	Washingtonian	10L
1811	Κουμ Κουατ Σακούλι	\N	Σακούλι	2025-04-01 18:36:02.464579	2025-04-01 18:36:02.464582	Καρποφώρα	\N	Σακούλι
1812	Κουμ Κουατ Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 18:36:02.690958	2025-04-01 18:36:02.690961	Καρποφώρα	\N	Σακούλι 12L
1813	Κυδωνιά Σακούλι	\N	Σακούλι	2025-04-01 18:36:02.916994	2025-04-01 18:36:02.916997	Καρποφώρα	\N	Σακούλι
1814	Κυδωνιά Σακούλι 12L	\N	Σακούλι 12L	2025-04-01 18:36:03.144297	2025-04-01 18:36:03.144301	Καρποφώρα	\N	Σακούλι 12L
1815	Αρχοντοφοίνικας C	\N	Archontophoenix alexander 15L	2025-04-01 18:36:03.670721	2025-04-01 18:36:03.670724	Φοινικοειδή	Archontophoenix alexander	15L
1816	Χαμαίρωπας Humilis 20L	\N	Chamaerops Humilis 20L	2025-04-01 18:36:03.895521	2025-04-01 18:36:03.895523	Φοινικοειδή	Chamaerops Humilis	20L
1819	Βραχυχίτων 2L	\N	Brachychiton acerifolius 2L	2025-04-01 19:55:45.729626	2025-04-01 19:55:45.729631	\N	Brachychiton acerifolius	2L
1821	Φλαμπουαγιά	\N	Spathodea campanulata None	2025-04-01 19:55:47.06218	2025-04-01 19:55:47.062186	\N	Spathodea campanulata	\N
1822	Τιπουάνα	\N	None None	2025-04-01 19:55:47.694631	2025-04-01 19:55:47.694637	\N	\N	\N
1823	Magnolia Grandiflora Μακνόλια	\N	None None	2025-04-01 19:56:04.66074	2025-04-01 19:56:04.660747	\N	\N	\N
1825	Lavandula Pinata Λεβαντούλα 2L	\N	None 2L	2025-04-01 19:57:03.637309	2025-04-01 19:57:03.637315	\N	\N	2L
1828	Pittosporum Tobira ‘Nanum’ Πιττόσπορο Νάνο 2L	\N	None 2L	2025-04-01 19:57:06.384807	2025-04-01 19:57:06.384813	\N	\N	2L
1830	Φυλλοβόλα Τασπιν	\N	None None	2025-04-01 19:57:07.669156	2025-04-01 19:57:07.669163	\N	\N	\N
1832	Elaeagnus Pungens Ελαίαγνος 5L	\N	None 5L	2025-04-01 19:57:23.974014	2025-04-01 19:57:23.974022	\N	\N	5L
1836	Philodendron xanadu	\N	Philodendron xanadu None	2025-04-01 19:57:47.093409	2025-04-01 19:57:47.093415	\N	Philodendron xanadu	\N
1837	Αρέκα	\N	Dypsis lutescens None	2025-04-01 19:57:47.786555	2025-04-01 19:57:47.78656	\N	Dypsis lutescens	\N
1839	Τριανταφυλιά Στεμ	\N	None None	2025-04-01 19:57:49.443258	2025-04-01 19:57:49.443266	\N	\N	\N
1840	Syzygium Συζύγιο 5L	\N	None 5L	2025-04-01 19:57:50.480724	2025-04-01 19:57:50.480729	\N	\N	5L
1841	Brahea Armata Brahea Armata 15L	\N	None 15L	2025-04-01 19:57:51.108099	2025-04-01 19:57:51.108106	\N	\N	15L
1842	Δράκαινα	\N	None None	2025-04-01 19:57:51.73402	2025-04-01 19:57:51.734025	\N	\N	\N
1817	Πενισετουμ Κόκκινο	None	Pennisetum setaceum 'Rubrum' 	2025-04-01 19:31:06.774345	2025-04-01 20:07:52.886251	None	Pennisetum setaceum	2L
1835	Alocasia Macrorrhiza	\N	Alocasia Macrorrhiza	2025-04-01 19:57:46.008704	2025-04-01 20:15:35.045966	None	None	None
1834	Λαντάνα	\N	Lantana	2025-04-01 19:57:45.378974	2025-04-01 20:19:14.254846	\N	\N	2L
1846	Εχιουμ 5L	\N	Echium candicans	2025-04-02 11:30:12.367122	2025-04-02 11:31:15.767092	\N	\N	5L
1845	Κισσός δίχρωμος	\N	Hedera helix 	2025-04-02 11:30:11.710916	2025-04-02 11:32:07.569055	\N	\N	2L
1847	ΜερσινιαΨυντρόφυλλη	\N	Myrtus communis microphylla	2025-04-02 12:25:48.355907	2025-04-02 12:26:44.324838	\N	Myrtus communis microphylla	2L
1849	Schinus Σχοινια 2L	\N	None 2L	2025-04-04 14:51:00.453561	2025-04-04 14:51:00.453566	\N	\N	2L
1850	Καβάφα Κόκκινη 3L	\N	None 3L	2025-04-04 14:51:01.394193	2025-04-04 14:51:01.394196	\N	\N	3L
1851	Μηλιά 3L	\N	None 3L	2025-04-04 14:51:02.329304	2025-04-04 14:51:02.329308	\N	\N	3L
1852	Αχλαδιά	\N	None None	2025-04-04 14:51:03.263746	2025-04-04 14:51:03.26375	\N	\N	\N
1854	Φορμόζα 3L	\N	None 3L	2025-04-04 14:51:06.302064	2025-04-04 14:51:06.302067	\N	\N	3L
1855	Black Diamond 3L	\N	None 3L	2025-04-04 14:51:07.240734	2025-04-04 14:51:07.240738	\N	\N	3L
1856	Bebeco 3L	\N	None 3L	2025-04-04 14:51:08.175039	2025-04-04 14:51:08.175043	\N	\N	3L
1857	Παπάγια	\N	None None	2025-04-04 14:51:09.105872	2025-04-04 14:51:09.105875	\N	\N	\N
1858	Κλήμα Superior	\N	Vitis vinifera None	2025-04-04 14:51:10.059186	2025-04-04 14:51:10.059189	\N	Vitis vinifera	\N
1861	Grapefruit 3L	\N	None 3L	2025-04-04 14:51:12.884843	2025-04-04 14:51:12.884846	\N	\N	3L
1862	Συκαμιά Κόκκινη 3L	\N	None 3L	2025-04-04 14:51:13.818997	2025-04-04 14:51:13.819001	\N	\N	3L
1863	Μεσπηλιά Καραντόκι 3L	\N	None 3L	2025-04-04 14:51:14.753981	2025-04-04 14:51:14.753985	\N	\N	3L
1864	Μοσφηλιά Ήμερη	\N	None None	2025-04-04 14:51:15.689411	2025-04-04 14:51:15.689415	\N	\N	\N
1865	Μοσφηλιά 3L	\N	None 3L	2025-04-04 14:51:16.621179	2025-04-04 14:51:16.621183	\N	\N	3L
1867	Ροπελινη  Size A	\N	Phoenix roebelenii None	2025-04-04 14:51:18.487439	2025-04-04 14:51:18.487443	\N	Phoenix roebelenii	\N
1859	Μανταρινιά Νόβα 3L	\N	None 3L	2025-04-04 14:51:11.016147	2025-04-04 14:52:20.791977	\N	\N	3L
1860	Grapefruit Κόκκινα 3L	\N	None 3L	2025-04-04 14:51:11.950161	2025-04-04 14:52:33.671457	\N	\N	3L
1868	Μανταρινιά Κλεμεντίνη 7L	\N	\N	2025-04-04 14:54:29.901743	2025-04-04 14:54:29.901747	\N	Μανταρινιά Κλεμεντίνη 7L	\N
1869	Κλήμα Βέρικο 2L	\N	\N	2025-04-04 14:54:30.344726	2025-04-04 14:54:30.34473	\N	Vitis vinifera	\N
1871	Μηλιά 3L	\N	\N	2025-04-04 14:54:31.309662	2025-04-04 14:54:31.309666	\N	Μηλιά 3L	\N
1873	Γιασεμί 2L	\N	\N	2025-04-04 14:54:32.191459	2025-04-04 14:54:32.191463	\N	Jasminum Officinale	\N
1874	Φορμόζα 3L	\N	\N	2025-04-04 14:54:32.779997	2025-04-04 14:54:32.780001	\N	Φορμόζα 3L	\N
1877	Παπάγια	\N	\N	2025-04-04 14:54:34.101594	2025-04-04 14:54:34.101599	\N	Παπάγια	\N
1878	Πορτοκαλιά Σιεκκέρικα 3L	\N	\N	2025-04-04 14:54:34.617291	2025-04-04 14:54:34.617296	\N	Πορτοκαλιά Σιεκκέρικα 3L	\N
1879	Μανταρινιά Νόβα 3L	\N	\N	2025-04-04 14:54:35.067138	2025-04-04 14:54:35.067141	\N	Μανταρινιά Νόβα 3L	\N
1880	Μανταρινιά Κλεμεντίνη 3L	\N	\N	2025-04-04 14:54:35.511511	2025-04-04 14:54:35.511515	\N	Μανταρινιά Κλεμεντίνη 3L	\N
1883	Συκαμιά Κόκκινη 3L	\N	\N	2025-04-04 14:54:36.843251	2025-04-04 14:54:36.843255	\N	Συκαμιά Κόκκινη 3L	\N
1884	Μεσπηλιά Καραντόκι 3L	\N	\N	2025-04-04 14:54:37.28442	2025-04-04 14:54:37.284424	\N	Μεσπηλιά Καραντόκι 3L	\N
1885	Μοσφηλιά Ήμερη	\N	\N	2025-04-04 14:54:37.722059	2025-04-04 14:54:37.722062	\N	Μοσφηλιά Ήμερη	\N
1886	Μοσφηλιά 3L	\N	\N	2025-04-04 14:54:38.160304	2025-04-04 14:54:38.160309	\N	Μοσφηλιά 3L	\N
1887	Στρελίτσια Reginae 2L Μονη	\N	\N	2025-04-04 14:54:38.601663	2025-04-04 14:54:38.601666	\N	Strelitzia reginae	\N
1888	Καβάφα Κόκκινη 3L	\N	\N	2025-04-04 15:03:01.322739	2025-04-04 15:03:01.322743	\N	Καβάφα Κόκκινη 3L	\N
1889	Αχλαδιά	\N	\N	2025-04-04 15:03:01.829979	2025-04-04 15:03:01.829984	\N	Αχλαδιά	\N
1890	Βιβούρνο Τίνους 2L	\N	\N	2025-04-04 15:03:02.336759	2025-04-04 15:03:02.336763	\N	Viburnum tinus	\N
1891	Βουκεμβίλια 5L	\N	\N	2025-04-04 15:03:02.7679	2025-04-04 15:03:02.767905	\N	Bougainvillea	\N
1892	Black Diamond 3L	\N	\N	2025-04-04 15:03:03.274396	2025-04-04 15:03:03.2744	\N	Black Diamond 3L	\N
1893	Bebeco 3L	\N	\N	2025-04-04 15:03:03.70549	2025-04-04 15:03:03.705496	\N	Bebeco 3L	\N
1894	Grapefruit Κόκκινα 3L	\N	\N	2025-04-04 15:03:04.510611	2025-04-04 15:03:04.510614	\N	Grapefruit Κόκκινα 3L	\N
1895	Grapefruit 3L	\N	\N	2025-04-04 15:03:04.942316	2025-04-04 15:03:04.942321	\N	Grapefruit 3L	\N
1896	Λευλάντι 10L	\N	\N	2025-04-04 15:26:56.750445	2025-04-04 15:26:56.750449	\N	Cupressus × leylandii	\N
1897	Ρυγχόσπερμο 2L	\N	\N	2025-04-04 15:26:57.110754	2025-04-04 15:26:57.110758	\N	Trachelospermum jasminoides	\N
1898	Γιαννής 2L	\N	\N	2025-04-04 15:26:57.376872	2025-04-04 15:26:57.376877	\N	Bougainvillea	\N
1899	Πακιστανός 2L	\N	\N	2025-04-04 15:26:57.645755	2025-04-04 15:26:57.645759	\N	Cestrum nocturnum  L	\N
1900	Στρελίτσια Reginae 5L Μονη	\N	\N	2025-04-04 15:26:57.91126	2025-04-04 15:26:57.911264	\N	Strelitzia reginae	\N
1901	Στρελίτσια Reginae (2pcs) 10L	\N	\N	2025-04-04 15:26:58.17606	2025-04-04 15:26:58.176064	\N	Strelitsia Reginae	\N
1902	Βουκεμβίλια 2L	\N	\N	2025-04-04 15:27:12.908441	2025-04-04 15:27:12.908446	\N	Bougainvillea	\N
1903	Συκιά Βαζανάτη	\N	\N	2025-04-04 15:27:25.713259	2025-04-04 15:27:25.713264	\N	ficus carica	\N
1904	Συκιά Βασιλικά	\N	\N	2025-04-04 15:27:25.982463	2025-04-04 15:27:25.982467	\N	Ficus Carica	\N
1905	Συκιά Bianco	\N	\N	2025-04-04 15:27:26.255676	2025-04-04 15:27:26.25568	\N	Συκιά Bianco	\N
1906	Ροδιά	\N	\N	2025-04-04 15:27:26.521008	2025-04-04 15:27:26.521012	\N	Punica granatum	\N
1907	Πορτοκαλιά Μέρλιν 3L	\N	\N	2025-04-04 15:27:26.834509	2025-04-04 15:27:26.834513	\N	Πορτοκαλιά Μέρλιν 3L	\N
1908	Λεμονιά Eureka	\N	\N	2025-04-04 15:27:27.102808	2025-04-04 15:27:27.102812	\N	Λεμονιά Eureka	\N
1909	Κουμ Κουατ	\N	\N	2025-04-04 15:27:27.41321	2025-04-04 15:27:27.413214	\N	Κουμ Κουατ	\N
1910	Lime 3L	\N	\N	2025-04-04 15:27:27.716992	2025-04-04 15:27:27.716997	\N	Lime 3L	\N
1911	Μανταρινιά Αρακαπά 3L	\N	\N	2025-04-04 15:27:27.982707	2025-04-04 15:27:27.982712	\N	Μανταρινιά Αρακαπά 3L	\N
1912	Dragon fruit	\N	\N	2025-04-04 15:27:28.255757	2025-04-04 15:27:28.255762	\N	Selenicereus undatus	\N
1913	Πόμελο Άσπρο 3L	\N	\N	2025-04-04 15:27:28.527526	2025-04-04 15:27:28.52753	\N	Πόμελο Άσπρο 3L	\N
1914	Πόμελο Κόκκινο 3L	\N	\N	2025-04-04 15:27:28.794831	2025-04-04 15:27:28.794835	\N	Πόμελο Κόκκινο 3L	\N
1915	Τουράντα Gold 2L	\N	\N	2025-04-04 15:27:29.061818	2025-04-04 15:27:29.061823	\N	Duranta erecta 'Gold Mound'	\N
1916	Πασχαλιά	\N	\N	2025-04-04 15:27:44.171838	2025-04-04 15:27:44.171843	\N	Syringa vulgaris	\N
1917	Φίκος Μπέντζαμιν	\N	\N	2025-04-04 15:27:44.436984	2025-04-04 15:27:44.436989	\N	Ficus benjamina	\N
1918	Λαντάνα	\N	\N	2025-04-04 15:27:44.799116	2025-04-04 15:27:44.79912	\N	Lantana	\N
1919	Κάρισσα Νάνα 2L	\N	\N	2025-04-04 15:27:45.080235	2025-04-04 15:27:45.08024	\N	Carissa macrocarpa 'Nana'	\N
1920	Μερσινια Ψυντρόφυλλη 2L	\N	\N	2025-04-04 15:27:45.348029	2025-04-04 15:27:45.348033	\N	Myrtus communis microphylla nana	\N
1921	Μερσίνια Άσπρα 2L	\N	\N	2025-04-04 15:27:45.613897	2025-04-04 15:27:45.613902	\N	Myrtus communis	\N
1922	Βιολέττα	\N	\N	2025-04-04 15:32:15.1508	2025-04-04 15:32:15.150804	\N	Βιολέττα	\N
1923	Ζαντόξυλο 5L	\N	\N	2025-04-04 15:32:15.470506	2025-04-04 15:32:15.470511	\N	Zantoxylum	\N
1924	Ιβύσκος Τηλεανθέος 5L	\N	\N	2025-04-04 15:32:15.877217	2025-04-04 15:32:15.877221	\N	Hibiscus tiliaceus	\N
1925	Κεράκι (Χόγια) 2L	\N	\N	2025-04-04 15:32:37.956315	2025-04-04 15:32:37.95632	\N	Hoya carnosa	\N
1926	Κοράλι Κόκκινο 2L	\N	\N	2025-04-04 15:32:38.322227	2025-04-04 15:32:38.322232	\N	Russelia equisetiformis	\N
1927	Διέτης 2L	\N	\N	2025-04-04 15:32:38.640294	2025-04-04 15:32:38.640298	\N	Dietes bicolor	\N
1928	Ελαίαγνος 5L	\N	\N	2025-04-04 15:34:32.804174	2025-04-04 15:34:32.804179	\N	Elaeagnus Pungens	\N
1929	Ελαίαγνος 2L	\N	\N	2025-04-04 15:34:33.075037	2025-04-04 15:34:33.075042	\N	Elaeagnus Pungens	\N
1930	Ελαίαγνος Πράσινος 2L	\N	\N	2025-04-04 15:34:33.341306	2025-04-04 15:34:33.34131	\N	Elaeagnus Ebbingei	\N
1931	Αροδάφνη 2L	\N	\N	2025-04-04 15:34:33.651413	2025-04-04 15:34:33.651418	\N	Nerium oleander	\N
1932	Λιμονιουμ 2L	\N	\N	2025-04-06 12:55:44.548151	2025-04-06 12:55:44.548156	\N	Limonium peresil	\N
1933	Λεβάντα 2L	\N	\N	2025-04-06 13:42:42.932616	2025-04-06 13:42:42.93262	\N	Lavandula angustifolia	\N
1934	Σαντολίνα 2L	\N	\N	2025-04-06 13:42:43.248621	2025-04-06 13:42:43.248626	\N	Santolina chamaecyparissus	\N
1935	Συκαμιά Αρσενική 7L	\N	\N	2025-04-06 14:01:54.498442	2025-04-06 14:01:54.498447	\N	Συκαμιά Αρσενική 7L	\N
1936	Καρυδιά Μοχώκ	\N	\N	2025-04-06 14:01:54.754823	2025-04-06 14:01:54.754828	\N	Καρυδιά Μοχώκ	\N
1937	Κυπαρισσι πλαγιοκλωνο 2L	\N	\N	2025-04-06 14:01:55.051521	2025-04-06 14:01:55.051526	\N	Cupressus sempervirens horizontalis	\N
1938	Κρεβίλια 2L	\N	\N	2025-04-08 13:20:39.99822	2025-04-08 13:20:39.998225	\N	Grevillea Robusta	\N
1939	Κυπαρισσι Ορθοκλωνο Κίτρινο 2L	\N	\N	2025-04-08 13:20:40.263484	2025-04-08 13:20:40.26349	\N	Cupressus sempervirens golden	\N
1940	Στίπα 2L	\N	\N	2025-04-08 13:20:40.522838	2025-04-08 13:20:40.522843	\N	Stipa ten. Pony Tails	\N
1941	Μουράγια 2L	\N	\N	2025-04-08 13:20:40.910687	2025-04-08 13:20:40.910691	\N	Murraya paniculata	\N
1942	Κάρισσα Νάνα 5L	\N	\N	2025-04-08 13:20:41.258576	2025-04-08 13:20:41.25858	\N	Carissa macrocarpa 'Nana'	\N
1943	Σιεφλέρα  2L	\N	\N	2025-04-08 13:27:57.102643	2025-04-08 13:27:57.102648	\N	Schefflera arboricola	\N
1944	Ευώνυμο δίχρωμο 2L	\N	\N	2025-04-08 13:28:07.365968	2025-04-08 13:28:07.365973	\N	Euonymus fortunei 'Emerald 'n' Gold	\N
1945	Τουράντα Πράσινη  2L	\N	\N	2025-04-08 13:28:17.981688	2025-04-08 13:28:17.981693	\N	Duranta	\N
1946	Passion Fruit 2L	\N	\N	2025-04-08 13:28:18.317974	2025-04-08 13:28:18.317979	\N	Passiflora edulis	\N
1947	Αρεκάστρουμ Size A	\N	\N	2025-04-08 13:28:38.345705	2025-04-08 13:28:38.34571	\N	Syagrus romanzoffiana, the queen palm	\N
1948	Αρεκάστρουμ Size B	\N	\N	2025-04-08 13:28:38.640635	2025-04-08 13:28:38.64064	\N	Syagrus romanzoffiana	\N
1949	Passion Fruit 5L	\N	\N	2025-04-08 13:28:58.471918	2025-04-08 13:28:58.471924	\N	Passiflora edulis	\N
1950	Αρχοντοφοίνικας Size A	\N	\N	2025-04-08 13:29:26.055972	2025-04-08 13:29:26.055977	\N	Archontophoenix alexander	\N
1951	Αρχοντοφοίνικας Size C	\N	\N	2025-04-08 13:29:26.323545	2025-04-08 13:29:26.323549	\N	Archontophoenix alexander	\N
1952	Φούλι	\N	\N	2025-04-09 12:11:32.948941	2025-04-09 12:11:32.948945	\N	Arabian jasmine	\N
1953	Στεφανωτή 5L	\N	\N	2025-04-09 12:11:33.208801	2025-04-09 12:11:33.208807	\N	Stephanotis floribunda	\N
1954	Yesterday, Today, Tommorow 5L	\N	\N	2025-04-09 12:11:33.641932	2025-04-09 12:11:33.641937	\N	Brunfelsia pauciflora	\N
1955	Ευγενία Etna Fire 5L	\N	\N	2025-04-09 12:11:33.944688	2025-04-09 12:11:33.944692	\N	Eugenia uniflora etna fire	\N
1956	Γιασεμί Γαλλικό 2L	\N	\N	2025-04-09 12:11:34.203777	2025-04-09 12:11:34.203782	\N	Jasminum	\N
1957	Γκαούρα Άσπρη 2L	\N	\N	2025-04-09 12:11:51.113637	2025-04-09 12:11:51.113643	\N	Gaura	\N
1958	Γεράνια	\N	\N	2025-04-09 12:12:08.21383	2025-04-09 12:12:08.213835	\N	Γεράνια	\N
1959	Μηλιά Άννα	\N	None None	2025-04-11 15:51:49.175284	2025-04-11 15:51:49.175297	\N	\N	\N
1960	Πόμελο Άσπρο 3L	\N	None 3L	2025-04-11 15:51:49.773474	2025-04-11 15:51:49.77348	\N	\N	3L
1961	Avocado	\N	None None	2025-04-11 15:51:50.355578	2025-04-11 15:51:50.355583	\N	\N	\N
1963	Κουρώ 3L	\N	None 3L	2025-04-11 15:51:51.612267	2025-04-11 15:51:51.612272	\N	\N	3L
1966	Κλήμα Βέρικο 2L	\N	Vitis vinifera 2L	2025-04-11 15:51:53.735424	2025-04-11 15:51:53.73543	\N	Vitis vinifera	2L
1967	Μερσίνια Άσπρα 2L	\N	Myrtus communis 2L	2025-04-11 15:51:54.317391	2025-04-11 15:51:54.317395	\N	Myrtus communis	2L
1962	Πόμελο Κόκκινο 3L	\N	\N	2025-04-11 15:51:50.976955	2025-04-11 15:53:07.891293	\N	\N	3L
1964	Ευγενία Etna Fire	\N	Eugenia uniflora	2025-04-11 15:51:52.564193	2025-04-11 15:53:39.838286	\N	Eugenia uniflora	2L
1965	Ευγενία Etna Fire	\N	Eugenia uniflora	2025-04-11 15:51:53.150412	2025-04-11 15:54:23.698676	\N	Eugenia uniflora	5L
1968	TULBACHIA VIOLACEA Τουρπάτσια 2L	\N	None 2L	2025-04-17 16:39:36.729168	2025-04-17 16:39:36.729172	\N	\N	2L
1969	Gaura Γκάουρα Κόκκινη 2L	\N	None 2L	2025-04-17 16:39:39.724817	2025-04-17 16:39:39.724821	\N	\N	2L
1970	Ροπελίνη Size D	\N	Phoenix roebelenii None	2025-04-17 16:39:44.866431	2025-04-17 16:39:44.866435	\N	Phoenix roebelenii	\N
1971	totem Κυπαρισσι Τοτεμ 10L	\N	Cupressus sempervirens 10L	2025-04-17 16:39:49.829358	2025-04-17 16:39:49.829362	\N	Cupressus sempervirens	10L
1972	Thuja Θουγια 5L	\N	None 5L	2025-04-17 16:39:52.87822	2025-04-17 16:39:52.878224	\N	\N	5L
1973	Pennisetum Compr. White Flower Πενισέτο Πρασινο 2L	\N	None 2L	2025-04-17 16:39:55.920459	2025-04-17 16:39:55.920463	\N	\N	2L
1975	Ροπελίνη Size E	\N	Phoenix roebelenii None	2025-04-17 16:40:01.993445	2025-04-17 16:40:01.993448	\N	Phoenix roebelenii	\N
1976	Test			2025-04-18 16:32:22.568411	2025-04-18 16:32:22.568414		Phillyrea	2L
1977	Ελιά Στεμ	\N	\N	2025-04-29 12:38:41.777311	2025-04-29 12:38:41.777316	\N	Ελιά Στεμ	\N
1978	Σολάνο Στεμ	\N	\N	2025-04-29 12:55:19.80608	2025-04-29 12:55:19.806085	\N	Solanum	\N
1979	Φεστούκα Γκρίζα	\N	\N	2025-04-29 12:55:20.309252	2025-04-29 12:55:20.309257	\N	Festuca Cinerea Glauca	\N
\.


--
-- Data for Name: product_update_request; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.product_update_request (id, product_id, price_list_id, old_price, new_price, status, created_at, updated_at, source_file) FROM stdin;
3	457	236	19.99	21.5	Approved	2025-03-31 19:05:22.866124	2025-04-01 19:05:22.866124	March Import.xlsx
4	457	236	19.99	18.75	Rejected	2025-03-30 19:05:22.866124	2025-04-01 19:05:22.866124	February Import.xlsx
2	457	236	19.99	22.99	Rejected	2025-04-01 19:05:22.866124	2025-04-01 19:06:32.718689	Price Update Apr 2025.xlsx
1	457	236	19.99	24.99	Rejected	2025-04-01 19:05:14.953639	2025-04-01 19:06:39.592401	Test Import.xlsx
7	532	2400	8	3.5	Rejected	2025-04-01 19:32:22.418298	2025-04-01 19:32:36.501709	Invoice #1184
6	1817	2401	3	3.5	Rejected	2025-04-01 19:32:21.762088	2025-04-01 19:32:42.327718	Invoice #1184
5	1740	2402	55	30	Rejected	2025-04-01 19:32:21.102009	2025-04-01 19:32:52.789411	Invoice #1184
9	533	2424	20	10	Approved	2025-04-01 19:57:48.502857	2025-04-01 19:58:24.09053	Invoice #1458
10	532	2417	8	20	Rejected	2025-04-01 19:57:50.167224	2025-04-01 20:11:00.531217	Invoice #1458
14	532	2417	8	20	Rejected	2025-04-01 20:37:04.656302	2025-04-01 20:43:03.820761	Invoice #1458
13	532	2417	8	20	Rejected	2025-04-01 20:33:25.698732	2025-04-01 20:43:07.328164	Invoice #1458
11	532	2417	8	20	Rejected	2025-04-01 20:21:57.645448	2025-04-01 20:43:10.450278	Invoice #1458
12	532	2417	8	20	Rejected	2025-04-01 20:28:42.463827	2025-04-01 20:43:13.398649	Invoice #1458
\.


--
-- Data for Name: quotation; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.quotation (id, customer_id, quotation_number, quotation_date, total_amount, currency, notes, file_path, created_at, updated_at, status, valid_until, viewed_at, accepted_at, rejected_at, order_id) FROM stdin;
28	24	PAK-2025-012	2025-04-14	618	€		\N	2025-04-14 15:53:46.829146	2025-05-25 11:32:32.42628	REJECTED	\N	\N	\N	\N	\N
27	23	PAK-2025-011	2025-04-11	3107.5	€		\N	2025-04-11 18:09:37.229294	2025-04-16 19:06:10.663472	SENT	\N	\N	\N	\N	\N
12	9	PAK-2025-002	2025-04-05	1401.5	€		quotation_PAK-2025-002_fabb318c.pdf	2025-04-05 11:51:39.07809	2025-05-26 17:24:25.072748	COMPLETED	\N	\N	2025-05-20 19:13:41.995863	\N	\N
30	25	PAK-2025-014	2025-04-15	779	€		quotation_PAK-2025-014_0b07d360.pdf	2025-04-15 11:24:46.953287	2025-04-19 11:57:03.91819	COMPLETED	\N	\N	\N	\N	\N
26	15	PAK-2025-010	2025-04-10	1505	€		\N	2025-04-10 03:28:30.648749	2025-04-19 18:04:37.680113	COMPLETED	\N	\N	\N	\N	\N
25	21	PAK-2025-009	2025-04-09	239.5	€		\N	2025-04-09 14:35:23.076241	2025-04-19 18:05:13.417957	COMPLETED	\N	\N	\N	\N	\N
24	1	PAK-2025-008	2025-04-09	311	€	Να παραδοθεί το Σάββατο 12/04/2025	\N	2025-04-09 11:47:57.810666	2025-04-19 18:06:01.275331	COMPLETED	\N	\N	\N	\N	\N
13	9	PAK-2025-003	2025-04-05	10103.75	€		quotation_PAK-2025-003_d3df3c41.pdf	2025-04-05 15:42:24.967008	2025-04-19 18:08:26.810708	SENT	\N	\N	\N	\N	\N
20	20	PAK-2025-007	2025-04-07	576	€		quotation_PAK-2025-007_be07492d.pdf	2025-04-07 18:07:07.825144	2025-05-20 19:20:36.853187	COMPLETED	2025-06-19	2025-05-20 19:20:28.621281	2025-05-20 19:20:36.853187	\N	\N
14	1	PAK-2025-004	2025-04-05	445.75	€		quotation_PAK-2025-004_af6d7202.pdf	2025-04-05 19:26:59.290433	2025-05-23 15:33:19.377626	COMPLETED	\N	\N	2025-05-23 15:33:19.377626	\N	\N
29	24	PAK-2025-013	2025-04-14	2565	€		\N	2025-04-14 16:12:44.01214	2025-05-25 11:32:03.166563	REJECTED	\N	\N	\N	\N	\N
56	38	PAK-2025-026	2025-05-18	2295	€		\N	2025-05-18 09:42:12.28275	2025-05-20 19:14:41.800727	COMPLETED	2025-06-19	2025-05-20 19:14:34.797115	2025-05-20 19:14:41.800727	\N	\N
55	34	PAK-2025-025	2025-05-15	180	€		\N	2025-05-15 13:26:18.745232	2025-05-20 19:15:08.55058	COMPLETED	2025-06-19	2025-05-20 19:15:01.862089	2025-05-20 19:15:08.55058	\N	\N
11	9	PAK-2025-001	2025-04-05	1510.1999999999998	€		quotation_PAK-2025-001_f2f85a1c.pdf	2025-04-05 11:31:44.057963	2025-04-24 20:06:10.434191	COMPLETED	\N	\N	\N	\N	\N
52	1	PAK-2025-022	2025-05-12	2873.5	€		\N	2025-05-12 17:24:16.317049	2025-05-20 19:15:42.006332	SENT	2025-06-19	2025-05-20 19:15:42.006332	\N	\N	\N
50	36	PAK-2025-021	2025-05-09	525	€		\N	2025-05-09 18:11:41.231114	2025-05-20 19:16:25.295511	COMPLETED	2025-06-19	2025-05-20 19:16:18.631102	2025-05-20 19:16:25.295511	\N	\N
45	1	PAK-2025-016	2025-04-29	106	€		\N	2025-04-29 17:52:57.613625	2025-05-23 15:37:12.962498	COMPLETED	2025-06-19	2025-05-20 19:25:43.98153	2025-05-23 15:37:12.962498	\N	\N
49	1	PAK-2025-020	2025-05-07	1428.75	€		\N	2025-05-07 18:22:30.990352	2025-05-20 19:17:00.413266	ACCEPTED	2025-06-19	2025-05-20 19:16:52.11334	2025-05-20 19:17:00.413266	\N	\N
48	1	PAK-2025-019	2025-05-07	518.75	€		quotation_PAK-2025-019_59016ec6.pdf	2025-05-07 14:20:31.71911	2025-05-20 19:17:50.7215	SENT	2025-06-19	2025-05-20 19:17:50.7215	\N	\N	\N
47	35	PAK-2025-018	2025-05-03	2739.5	€		\N	2025-05-03 13:29:22.50751	2025-05-20 19:18:45.309136	SENT	2025-06-19	2025-05-20 19:18:45.309136	\N	\N	\N
62	38	PAK-2025-029	2025-05-22	1617.5	€		\N	2025-05-22 17:23:34.827769	2025-05-24 08:13:08.351494	COMPLETED	2025-06-21	2025-05-22 18:29:31.68612	2025-05-22 18:29:37.689181	\N	\N
44	33	PAK-2025-015	2025-04-27	542.5	€		\N	2025-04-27 07:29:44.52794	2025-05-20 19:19:56.833697	COMPLETED	2025-06-19	2025-05-20 19:19:44.772265	2025-05-20 19:19:56.833697	\N	\N
15	1	PAK-2025-005	2025-04-05	1330	€		quotation_PAK-2025-005_b91e129e.pdf	2025-04-05 20:58:49.257268	2025-05-01 19:37:03.957901	ACCEPTED	\N	\N	\N	\N	\N
54	37	PAK-2025-024	2025-05-15	278.3	€		quotation_PAK-2025-024_9bafb102.pdf	2025-05-15 12:47:32.392254	2025-05-20 19:24:44.093414	SENT	2025-06-19	2025-05-20 19:24:44.093414	\N	\N	\N
46	1	PAK-2025-017	2025-04-30	5423.5	€	1) Τα λιγούστρο είναι σε περιορισμένη ποσότητα\r\n2) Date Palms ο παραγωγός δεν μπορεί να μας εγγυηθεί ότι θα κάνουν καρπό\r\n3) Τα σέλουμ θα είναι διαθέσιμα σε 1,5 μήνα	\N	2025-04-30 12:29:46.522934	2025-05-20 19:26:47.092159	SENT	2025-06-19	2025-05-20 19:26:47.092159	\N	\N	\N
53	7	PAK-2025-023	2025-05-14	492.5	€		quotation_PAK-2025-023_91e94915.pdf	2025-05-14 14:04:21.652247	2025-05-21 13:02:03.91039	SENT	2025-06-20	2025-05-21 13:01:34.653943	\N	\N	\N
58	40	PAK-2025-028	2025-05-19	2702.5	€		\N	2025-05-19 13:23:44.782379	2025-05-27 08:37:57.812983	SENT	2025-06-20	2025-05-21 20:21:34.951049	\N	\N	\N
57	39	PAK-2025-027	2025-05-19	411	€		\N	2025-05-19 09:45:44.562226	2025-05-19 09:45:45.375685	created	\N	\N	\N	\N	\N
66	45	PAK-2025-031	2025-05-28	187.75	€		\N	2025-05-28 18:40:51.553443	2025-05-28 18:52:28.268224	SENT	2025-06-27	2025-05-28 18:52:28.268224	\N	\N	\N
65	9	PAK-2025-030	2025-05-25	1755.5	€		\N	2025-05-25 10:48:53.746112	2025-05-28 18:55:00.779434	ACCEPTED	2025-06-24	2025-05-25 11:27:54.155267	2025-05-28 18:55:00.779434	\N	\N
67	45	PAK-2025-032	2025-05-28	366.5	€		\N	2025-05-28 18:56:11.565734	2025-05-28 19:01:48.488591	SENT	2025-06-27	2025-05-28 19:01:48.488591	\N	\N	\N
\.


--
-- Data for Name: quotation_item; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.quotation_item (id, quotation_id, product_id, description, scientific_name, pot_size, quantity, selling_price, vat_rate, supplier, cost_price, total, height, supplier_id, "position", delivery_status, supplier_order_status, delivery_date, supplier_order_date, supplier_order_reference) FROM stdin;
356	13	\N	Myrtus communis 'Nana'	Myrtus communis 'Nana'	5L	17	10	19	In-house Production	0	170	30cm	\N	20	PENDING	NOT_ORDERED	\N	\N	\N
569	26	\N	Καλλιτρίδα	Καλλιτρίδα	1,5μ	40	15	19	Tsimouris	0	600	1,5μ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
349	13	\N	ΣΤΙΠΑ	Stipa tenuissima	2L	48	4.5	19	Arocaria	2.5	216	30cm	4	13	PENDING	NOT_ORDERED	\N	\N	\N
570	26	464	Αροδάφνη	Αροδάφνη	1μ	70	3	19	In-house Production	0	210	1μ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
358	13	1828	Pittosporum tobira	Pittosporum tobira	2L/50cm	27	4.5	19	In-house Production	0	121.5	60/80cm	\N	22	PENDING	NOT_ORDERED	\N	\N	\N
359	13	\N	Pittosporum tobira 'Nana'	Pittosporum tobira 'Nana'	5L	78	18.5	19	Panayiotou	10	1443	30cm	\N	23	PENDING	NOT_ORDERED	\N	\N	\N
350	13	\N	Tulbaghia violacea	Tulbaghia violacea	2L	56	3.5	19	Ginger	0	196	30cm	14	14	PENDING	NOT_ORDERED	\N	\N	\N
352	13	\N	Carissa macrocarpa 'Green Carpet'	Carissa macrocarpa 'Green Carpet'	5L	15	9	19	In-house Production	0	135	30cm	\N	16	PENDING	NOT_ORDERED	\N	\N	\N
360	13	1790	Viburnum tinus	Viburnum tinus	5L/50cm	24	12.5	19	In-house Production	0	300	60/80cm	\N	24	PENDING	NOT_ORDERED	\N	\N	\N
344	13	\N	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolia	2-2,5m/8-10G	3	54	19	Shaelos	35	162	10-12 Girth/200cm	3	8	PENDING	NOT_ORDERED	\N	\N	\N
345	13	\N	Pampas grass	Cortaderia selloana		4	12.5	19	In-house Production	0	50	60cm	2	9	PENDING	NOT_ORDERED	\N	\N	\N
361	13	\N	ΜΑΡΓΑΡΙΤΑ ΚΑΖΑΝΙΑ	Gazania tomentosa	2L	35	3.5	19	In-house Production	0	122.5	20cm	\N	25	PENDING	NOT_ORDERED	\N	\N	\N
353	13	525	Elaeagnus pungens	Elaeagnus pungens	5L	10	12	19	In-house Production	0	120	60/80cm	\N	17	PENDING	NOT_ORDERED	\N	\N	\N
346	13	1927	ΔΙΕΤΗΣ	Dietes bicolor	2L	35	4.5	19	In-house Production	0	157.5	30cm	2	10	PENDING	NOT_ORDERED	\N	\N	\N
337	13	\N	Archontophoenix alexandrae	Archontophoenix alexandrae	120cm	2	108	19	Moesis	60	216	150cm	5	1	PENDING	NOT_ORDERED	\N	\N	\N
347	13	\N	ΠΕΝΙΣΕΤΟΥΜ ΠΡΑΣΙΝΟΣ	Pennisetum alopecuroides	2L	22	4.5	19	In-house Production	0	99	50cm	2	11	PENDING	NOT_ORDERED	\N	\N	\N
338	13	1819	ΒΡΑΧΥΧΥΤΩΝ	Brachychiton acerifolius	10-12 Girth/170/200cm	9	78	19	Shaelos	50	702	10-12 Girth/170/200cm	3	2	PENDING	NOT_ORDERED	\N	\N	\N
354	13	\N	Fargesia robusta	Fargesia robusta	150cm	21	72	19	Chrymaris	45	1512	120/150cm	7	18	PENDING	NOT_ORDERED	\N	\N	\N
339	13	\N	ΣΥΚΑΣ	Cycas revoluta	12L	7	30	19	Panayiotou	18	210	60cm	6	3	PENDING	NOT_ORDERED	\N	\N	\N
362	13	1897	Trachelospermum jasminoides	Trachelospermum jasminoides	170cm	10	40	19	Shaelos	25	400	150-170cm	\N	26	PENDING	NOT_ORDERED	\N	\N	\N
348	13	\N	Pennisetum alopecuroides 'Little bunny'	Pennisetum alopecuroides 'Little bunny'	2L	25	7	19	Ginger	4	175	30cm	14	12	PENDING	NOT_ORDERED	\N	\N	\N
341	13	552	ΕΛΙΑ	Olea europaea		3	396	5	Arocaria	175	1188	14-16 Girth/200cm	4	5	PENDING	NOT_ORDERED	\N	\N	\N
355	13	\N	ΧΑΜΑΙΚΥΠΑΡΙΣΣΟ	Juniperus horizontalis	2L	19	5	19	In-house Production	0	95	50cm	\N	19	PENDING	NOT_ORDERED	\N	\N	\N
342	13	\N	ΠΛΟΥΜΕΡΙΑ ΛΕΥΚΗ	Plumeria alba	1.5m	2	72	19	Arocaria	45	144	170cm	4	6	PENDING	NOT_ORDERED	\N	\N	\N
557	24	\N	'SWANE'S GOLDEN	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'		1	15	19	Moesis	10	15	5L/80cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
558	24	530	Totem	Cupressus sempervirens totem		18	15	19	In-house Production	0	270	10L/1m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
363	13	1727	Lavandula angustifolia	Lavandula angustifolia	1L/15cm	23	3.75	19	Other	0	86.25	30cm	11	27	PENDING	NOT_ORDERED	\N	\N	\N
559	24	1825	Λεβαντούλα	Lavandula Pinata		3	2	5	Ginger	2	6	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
561	24	502	ΧΑΜΑΙΚΥΠΑΡΙΣΣΟ ΓΚΡΙΖΟ	Juniperus sp.		2	3	19	In-house Production	0	6	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
562	25	503	Χαμαικυπάρισσο Πράσινο	Chamaecyparis lawsoniana	2L	3	4	19	In-house Production	0	12	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
563	25	\N	Λαντάνα Έρπουσα	LANTANA  MONTEVIDENSIS	2L	15	3.5	19	Moesis	2.5	52.5	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
564	25	482	Duranta Gold	Duranta erecta	2L	10	4	19	In-house Production	0	40	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
565	25	468	Λαντάνα Θάμνος	Lantana Camara	2L	10	3.5	19	Moesis	2.5	35	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
566	25	457	Μαργαρίτα Ασημόφυλλη	Gazania rigens	2L	30	3	19	In-house Production	0	90	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
568	25	1726	Λασμαρί Foxtail	Rosmarinus Officinalis Prostratus	2L	5	2	5	In-house Production	0	10	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
571	26	\N	Συκαμια Αρσενική	Συκαμια Αρσενική	1,5μ	3	45	19	Moesis	0	135	1,5μ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
343	13	527	Ficus Amstel King	Ficus binnendijkii 'Amstel King'	180cm	29	55	19	Shaelos	35	1595	180cm	3	7	PENDING	NOT_ORDERED	\N	\N	\N
572	26	1743	Μαστιχόδεντρο	Μαστιχόδεντρο	1,7μ	24	20	19	In-house Production	0	480	1,7μ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
573	26	\N	Χαρουπιά	Χαρουπιά	1,5μ	4	20	19	Other	0	80	1,5μ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
574	27	\N	ΤΟΤΕΜ	Cypress sempervirens totem	1.1m	18	15	19	In-house Production	0	270	h ~ 1.4m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
593	28	\N	Καζουαρίνα	Καζουαρίνα		50	4	19	In-house Production	0	200	30cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
611	29	1743	Μαστιχόδεντρο	Μαστιχόδεντρο		50	35	19	Nevada 	0	1750	200 εκ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
579	27	\N	Χαμαικυπάρισσο Γκρίζο	Juniperus horizontalis gray		10	3.5	19	In-house Production	0	35	2.5 lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
583	27	\N	Μερσηνιά Ψιντρόφυλλη	Myrtus communis compacta		45	3	19	In-house Production	0	135	2.5 lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
298	11	\N	ΜΑΡΓΑΡΙΤΑ ΚΑΖΑΝΙΑ	Gazania tomentosa		8	2.5	19	In-house Production	0	20	20cm	\N	31	PENDING	NOT_ORDERED	\N	\N	\N
590	27	\N	Πιττόσπορο Νάνο	Pittosporum tobira nanum		6	3.5	19	In-house Production	0	21	2.5lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
591	27	1897	Ρυγχόσπερμο	Trachelospermum jasminoides		6	3.5	19	In-house Production	0	21	2.5lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
624	30	\N	Totem'	Cupressus  sempervirens	2M	10	45	19	Shaelos	35	450	2M	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
578	27	\N	Ροδιά	Punica granatun	8/10Girth-1.8m	1	135	19	Nevada 	0	135	30lt/1,8m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
588	27	\N	Γκαούρα Άσπρη	Gaura white		15	3.5	19	Arocaria	2.5	52.5	2.5 lt	4	0	PENDING	NOT_ORDERED	\N	\N	\N
577	27	\N	Λεμονιά	Lemon tree	1.8m	1	55	5	Nevada 	40	55	30 lt/1,8m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
575	27	\N	Μαστιχόδεντρο	Pistacia lentiscus	10L/2.5m	26	25	19	Nevada 	20	650	5lt	12	0	PENDING	NOT_ORDERED	\N	\N	\N
594	28	\N	Τερατσιές (αμαντιασμένες)	Τερατσιές (αμαντιασμένες)		15	8	5	In-house Production	0	120	80cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
595	28	\N	Φοινικιά Robelina	Φοινικιά Robelina		1	30	19	In-house Production	0	30	25cm h~κορμος	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
585	27	\N	Asparagus Meyeri	Asparagus Meyeri	5L	35	8	19	Nevada 	6	280	2.5 lt	12	0	PENDING	NOT_ORDERED	\N	\N	\N
596	28	\N	Κυπαρίσσι Totem Gold Gress	Κυπαρίσσι Totem Gold Gress		1	18	19	In-house Production	0	18	100 εκ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
597	28	\N	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)		8	10	19	In-house Production	0	80	130cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
598	28	1916	Πασχαλιά	Πασχαλιά		3	10	19	In-house Production	0	30	40cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
582	27	\N	Phillyrea	Phillyrea	10L	12	19.5	19	Nevada 	0	234	2.5 lt	12	0	PENDING	NOT_ORDERED	\N	\N	\N
599	28	\N	Αρτιμαθκιά	Αρτιμαθκιά		2	5	19	In-house Production	0	10	2L/1m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
600	28	\N	Φοινικιά Αεροκάστρουμ	Φοινικιά Αεροκάστρουμ		1	50	19	In-house Production	0	50	170cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
592	27	\N	Zoyssia grass	Zoyssia grass	2L	200	5	19	Shaelos	3.5	1000		3	0	PENDING	NOT_ORDERED	\N	\N	\N
601	28	\N	Ροδακινιά	Ροδακινιά		1	8	19	Chrysovalantis 	0	8	100cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
602	28	536	Δαμασκηνιά	Δαμασκηνιά		1	8	19	Chrysovalantis 	0	8	100cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
586	27	\N	Hyparrhenia hitra	Hyparrhenia hitra	2L	7	4.5	19	Nevada 	3	31.5	2.5 lt	12	0	PENDING	NOT_ORDERED	\N	\N	\N
603	28	1906	Ροδιά	Ροδιά		1	4	19	In-house Production	0	4	40cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
587	27	\N	Τριανταφυλιά Αναρρυγχώμενη Άσπρη (Παξιανή)	Rose white climbing		4	8	19	In-house Production	0	32	5lt	2	0	PENDING	NOT_ORDERED	\N	\N	\N
604	28	1749	Συκιά	Συκιά		1	4	5	In-house Production	0	4	40cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
580	27	\N	Αρκοελιά	Αρκοελιά	2L	7	5	19	Moesis	0	35	5lt	5	0	PENDING	NOT_ORDERED	\N	\N	\N
607	28	493	Αμυγδαλια	Αμυγδαλια		2	8	5	Chrysovalantis 	0	16	100cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
581	27	\N	Δάφνη	Laurus nobilis (Bay leaf)		9	4	19	Other	0	36	2.5 lt	11	0	PENDING	NOT_ORDERED	\N	\N	\N
608	28	\N	Σαγκουίνη	Σαγκουίνη		1	8	5	Chrysovalantis 	0	8	100cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
589	27	\N	Περόβσκια	Perovskia		7	3.5	5	Nevada 	2.5	24.5	2.5 lt	12	0	PENDING	NOT_ORDERED	\N	\N	\N
609	28	1878	Πορτοκαλιά	Πορτοκαλιά		1	8	5	Chrysovalantis 	0	8	100cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
610	28	1908	Λεμονιά	Λεμονιά		1	8	5	Chrysovalantis 	0	8	100cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
625	30	\N	Κυπαρίσσι Κιτρινο	Cupressus  sempervirens		5	15	19	In-house Production	0	75	1,5m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
606	28	\N	Μεσπιλιά	Μεσπιλιά		1	8	5	Chrysovalantis 	0	8	100cm	9	0	PENDING	NOT_ORDERED	\N	\N	\N
626	30	1797	Μερσυνια νανα	Myrtus communis microphylla nana	5L	15	10	19	In-house Production	0	150	5l	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
605	28	1859	Μανταρινιά	Μανταρινιά		1	8	5	Chrysovalantis 	0	8	100cm	9	0	PENDING	NOT_ORDERED	\N	\N	\N
612	29	\N	Φοινικιά Robelina	Φοινικιά Robelina		1	70	19	In-house Production	0	70	60cm h~ κορμός	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
613	29	\N	Κυπαρίσσι Totem Gold Gress	Κυπαρίσσι Totem Gold Gress		1	55	19	Shaelos	0	55	200 εκ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
614	29	\N	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)		8	55	19	Shaelos	0	440	200 εκ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
615	29	\N	Αρτιμαθκιά	Αρτιμαθκιά		2	35	19	In-house Production	0	70	200cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
627	30	\N	Λασμαρί Foxtail	Λασμαρί Foxtail	2L	10	2	5	In-house Production	0	20	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
628	30	535	Strelitzia Reginae	Strelitzia Reginae	10L/2pcs	2	12	19	In-house Production	0	24	10L/2pcs	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
629	30	\N	Μερσηνιά Stem	Myrtus Stem	15L	2	30	19	Shaelos	25	60	15L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
616	29	\N	Ροδακινιά	Ροδακινιά		1	20	5	Chrysovalantis 	0	20	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
617	29	536	Δαμασκηνιά	Δαμασκηνιά		1	20	5	Chrysovalantis 	0	20	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
618	29	1859	Μανταρινιά	Μανταρινιά		1	20	5	Chrysovalantis 	0	20	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
619	29	\N	Μεσπιλιά	Μεσπιλιά		1	20	5	Chrysovalantis 	0	20	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
620	29	493	Αμυγδαλια	Αμυγδαλια		2	20	5	Chrysovalantis 	0	40	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
269	11	\N	ΔΡΑΚΑΙΝΑ	Dracaena  marginata	3pcs	5	50	19	H&G	40	250	120/150cm	\N	2	PENDING	NOT_ORDERED	\N	\N	\N
621	29	\N	Σαγκουίνη	Σαγκουίνη		1	20	5	Chrysovalantis 	0	20	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
622	29	1878	Πορτοκαλιά	Πορτοκαλιά		1	20	5	Chrysovalantis 	0	20	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
623	29	1908	Λεμονιά	Λεμονιά		1	20	5	Chrysovalantis 	0	20	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
268	11	\N	ΤΟΤΕΜ	Cupressus  sempervirens	2m	2	45	19	Shaelos	35	90	170/200cm	\N	1	PENDING	NOT_ORDERED	\N	\N	\N
630	11	\N	Αλτερναθήρα	Alternathera Deata	15cm	6	3.5	19	Moesis	2.5	21	30cm	5	0	PENDING	NOT_ORDERED	\N	\N	\N
297	11	\N	ΓΙΑΝΝΗΣ	Bougainvillea glabra	2m	2	45	19	Shaelos	35	90	150-170cm	\N	30	PENDING	NOT_ORDERED	\N	\N	\N
717	49	1253	ΡΟΔΙΑ	PUNICA GRANATUM	10L	3	10	19	In-house Production	0	30		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
719	49	\N	ΣΤΙΠΑ	STIPA TENUISSIMA	2L	16	2.5	19	In-house Production	0	40		2	0	PENDING	NOT_ORDERED	\N	\N	\N
718	49	1725	Λασμαρί Foxtail	ROSMARINUS OFFICINALIS	2L	7	2	5	In-house Production	0	14		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
739	12	\N	Κονβολβουλος	Convolvulus cneorum	2L	16	4	19	Moesis	2.5	64		5	0	PENDING	NOT_ORDERED	\N	\N	\N
740	12	\N	Ρυγχόσπερμο	Trachelospermum jasminoides	2L/80cm	1	3.5	19	In-house Production	0	3.5		2	0	PENDING	NOT_ORDERED	\N	\N	\N
495	20	\N	Λευκόφυλλα πράσινα	Λευκόφυλλα πράσινα		7	4	19	Moesis	2.5	28		\N	6	PENDING	NOT_ORDERED	\N	\N	\N
496	20	\N	Τριανταφυλλιές διάφορα χρώματα	Τριανταφυλλιές διάφορα χρώματα		8	9	19	Shaelos	5.6	72	4L	\N	7	PENDING	NOT_ORDERED	\N	\N	\N
497	20	\N	Δεντρολίβανο	Δεντρολίβανο		5	2	5	In-house Production	0	10	2L	\N	8	PENDING	NOT_ORDERED	\N	\N	\N
498	20	1774	Θυμάρι	Θυμάρι		5	2	5	In-house Production	0	10	2L	\N	9	PENDING	NOT_ORDERED	\N	\N	\N
499	20	\N	Λεβάντες	Λεβάντες		5	2	5	In-house Production	0	10	2L	\N	10	PENDING	NOT_ORDERED	\N	\N	\N
742	52	\N	ΛΕΜΟΝΙΑ	Citrus limon	20L/150cm-170cm	1	40	5	Chrysovalantis 	0	40	8-10 Girth	9	0	PENDING	NOT_ORDERED	\N	\N	\N
745	52	\N	ΤΖΙΑΚΑΡΑΝΤΑ	Jacaranda mimosifolia	250cm/10-12 Girth	1	45	19	Shaelos	35	45	10-12 Girth	3	0	PENDING	NOT_ORDERED	\N	\N	\N
753	52	1253	ΡΟΔΙΑ	Punica granatum	100cm-120cm	1	20	19	In-house Production	0	20		2	0	PENDING	NOT_ORDERED	\N	\N	\N
752	52	\N	Κοκκινόφυλλη	Prunus pissardii 'Nigra'	200cm/6-8 Girth	3	60	19	Arocaria	45	180	10-12 Girth	4	0	PENDING	NOT_ORDERED	\N	\N	\N
756	52	524	ΑΓΑΠΑΝΘΟΣ	Agapanthus africanus	10cm	7	3.5	19	In-house Production	0	24.5	2-3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
750	52	533	Phoenix roebelenii	Phoenix roebelenii	70cm	3	70	19	In-house Production	0	210	100cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
754	52	1262	ΑΡΤΥΜΑΤΙΑ	Schinus molle	200-250cm/10-12Girth	2	100	19	Arocaria	75	200	10-12 Girth	4	0	PENDING	NOT_ORDERED	\N	\N	\N
755	52	\N	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolia	200-250cm/ 10-12 Girth	2	100	19	Arocaria	75	200	10-12 Girth	4	0	PENDING	NOT_ORDERED	\N	\N	\N
757	52	\N	Διανέλλα	Dianella tasmanica	30cm	12	8	19	Arocaria	6	96	2-3lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
775	53	489	Κάρισσα Νάνα	Κάρισσα Νάνα	2L	3	3	19	In-house Production	0	9		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
777	53	1727	Λεβάντα	Lavandula angustifolia Les Bleus Thierry	2L	2	2	5	In-house Production	0	4		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
793	54	1908	Λεμονιά Eureka	Λεμονιά Eureka		2	18	19	Panayiotou	0	36	7Λ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
794	54	\N	ΓΙΑΦΗΤΙΚΗ	ΓΙΑΦΗΤΙΚΗ		1	18	19	Panayiotou	0	18	7Λ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
744	52	\N	ΠΟΡΤΟΚΑΛΙΑ	Citrus sinensis	20L/150cm-170cm	1	40	5	Chrysovalantis 	20	40	8-10 Girth	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
743	52	\N	ΜΑΝΤΑΡΙΝΙΑ	Citrus reticulata	20L/150cm-170cm	1	40	5	Chrysovalantis 	20	40	8-10 Girth	9	0	PENDING	NOT_ORDERED	\N	\N	\N
751	52	\N	Plumeria alba	Plumeria alba	150cm	1	60	19	Arocaria	45	60	10-12 Girth	4	0	PENDING	NOT_ORDERED	\N	\N	\N
748	52	552	ΕΛΙΑ	Olea europaea	170cm/20-25 Girth	1	235	5	Arocaria	175	235		4	0	PENDING	NOT_ORDERED	\N	\N	\N
779	53	486	Ζαντόξυλο	Ζαντόξυλο	2L	6	4	19	In-house Production	0	24		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
738	12	\N	ΛΑΣΜΑΡΙ ΟΡΘΟΚΛΑΔΟ	Rosmarinus Officinalis	20cm	34	2	5		0	68		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
284	11	\N	ΚΑΡΙΣΣΑ ΝΑΝΑ	Carissa macrocarpa 'Green Carpet'	2L/10cm	10	3.5	19	In-house Production	0	35	30cm	\N	17	PENDING	NOT_ORDERED	\N	\N	\N
488	20	\N	Βιβούρνο (κοινό)	Βιβούρνο (κοινό)		10	3.5	19	In-house Production	0	35	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
489	20	\N	Ελαίαγνους	Ελαίαγνους		4	3.5	19	In-house Production	0	14	2L	\N	1	PENDING	NOT_ORDERED	\N	\N	\N
490	20	\N	Ελαίαγνους διχρωμο	Ελαίαγνους διχρωμο		4	3.5	19	In-house Production	0	14	2L	\N	2	PENDING	NOT_ORDERED	\N	\N	\N
491	20	\N	Ευώνυμο διχρωμο	Ευώνυμο διχρωμο		8	3.5	19	In-house Production	0	28	2L	\N	3	PENDING	NOT_ORDERED	\N	\N	\N
280	11	\N	ΤΟΥΡΠΑΤΣΙΑ	Tulbaghia violacea		16	2.5	19	In-house Production	0	40	30cm	\N	13	PENDING	NOT_ORDERED	\N	\N	\N
282	11	\N	ΑΛΟΗ ΒΕΡΑ	Aloe vera	5L	2	7	19	Arocaria	5	14	30cm	4	15	PENDING	NOT_ORDERED	\N	\N	\N
631	11	\N	Αεονιουμ 	aeonium	7L	5	15	19	Lakkotripi	8	75	7L	10	0	PENDING	NOT_ORDERED	\N	\N	\N
652	45	\N	Συκιά	Fig trees		2	3.5	5	In-house Production	0	7	2lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
653	45	\N	Αγάπανθος	Agapanthus		5	3.5	19	In-house Production	0	17.5	2lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
633	11	\N	Χαμέροπς	Chamaerops humilis		5	40	19	In-house Production	0	200		2	0	PENDING	NOT_ORDERED	\N	\N	\N
634	11	\N	Αλοκάσια	Alocasia		2	40	19	Shaelos	0	80		3	0	PENDING	NOT_ORDERED	\N	\N	\N
635	44	\N	ΣΥΚΙΑ ΛΑΪΚΙΑΝΗ	ΣΥΚΙΑ ΛΑΪΚΙΑΝΗ		1	3.5	5	In-house Production	0	3.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
637	44	\N	ΜΑΓΝΟΛΙΕΣ	ΜΑΓΝΟΛΙΕΣ		2	80	19	Shaelos	0	160		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
638	44	\N	ΚΙΤΡΟΜΗΛΙΑ	ΚΙΤΡΟΜΗΛΙΑ		1	6	5	In-house Production	0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
639	44	\N	ΚΕΡΑΣΙΕΣ ΓΙΑ ΗΜΙΟΡΕΙΝΑ	ΚΕΡΑΣΙΕΣ ΓΙΑ ΗΜΙΟΡΕΙΝΑ		6	8	5	Chrysovalantis 	0	48		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
640	44	\N	ΦΟΙΝΙΚΙΕΣ ΑΠΕΚΑΣΤΡΩΜΕΝΕΣ (ΛΙΓΟ ΜΕΓΑΛΕΣ)	ΦΟΙΝΙΚΙΕΣ ΑΠΕΚΑΣΤΡΩΜΕΝΕΣ (ΛΙΓΟ ΜΕΓΑΛΕΣ)		4	35	19	In-house Production	0	140		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
654	45	\N	Κάρυ	Helichrysum italicum		5	2	5	In-house Production	0	10	2lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
493	20	\N	Ευγένιες	Ευγένιες		10	10	19	Arocaria	6	100	4L	\N	4	PENDING	NOT_ORDERED	\N	\N	\N
316	12	\N	ΠΕΝΙΣΕΤΟΥΜ ΠΡΑΣΙΝΟ	Pennisetum alopecuroides	2L	2	3.5	19	In-house Production	0	7	50cm	\N	12	PENDING	NOT_ORDERED	\N	\N	\N
494	20	\N	Μετροσίδηρους	Μετροσίδηρους		13	3.5	19	In-house Production	0	45.5	2L	\N	5	PENDING	NOT_ORDERED	\N	\N	\N
655	45	1266	Μαστιχόδεντρο	Schinus terebinthifolius		3	3.5	19	In-house Production	0	10.5	2lt	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
651	45	\N	Πεύκος Ήμερος	Pinus pinea		1	26	19	Arocaria	20	26	1,7m	4	0	PENDING	NOT_ORDERED	\N	\N	\N
650	45	\N	Τζιακαράντα	Jacaranda 		1	35	19	Arocaria	25	35	2m	4	0	PENDING	NOT_ORDERED	\N	\N	\N
657	44	\N	Συκαμιά Άσπρη Μακρή			1	8	5	Chrysovalantis 	0	8		9	0	PENDING	NOT_ORDERED	\N	\N	\N
656	44	\N	Συκαμιά Κόκκινο Κοντό		Σακκούλη	1	8	5	Chrysovalantis 	0	8		9	0	PENDING	NOT_ORDERED	\N	\N	\N
636	44	\N	Συκαμιά Κόκκινο Μακρή			1	8	5	Chrysovalantis 	0	8		9	0	PENDING	NOT_ORDERED	\N	\N	\N
658	46	\N	Ευγενία Etna Fire 	Eugenia Etna Fire 	160cm	100	22	19	Shaelos	20	2200	180 cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
659	46	\N	Πιττόσπορα Νάνα	Pittosporum Nana 		24	3	19	In-house Production	0	72	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
662	46	1809	Χαμαίρωπας	Chamaerops Humilis	70cm	8	45	19	In-house Production	0	360	70cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
669	15	\N	ΡΟΔΙΑ	PUNICA GRANATUM	ΤΑΣΠΙΝ	1	15	5	Moesis	10	15		5	0	PENDING	NOT_ORDERED	\N	\N	\N
274	11	\N	ΔΙΕΤΗΣ	Dietis bicolor	2L	18	3.5	19	In-house Production	5	63	30cm	2	7	PENDING	NOT_ORDERED	\N	\N	\N
642	44	\N	ΑΓΙΟΚΛΗΜΑ	ΑΓΙΟΚΛΗΜΑ		1	4	19	In-house Production	0	4		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
644	44	\N	ΓΑΡΔΕΝΙΑ ΔΕΝΤΡΟ (ΟΧΙ ΦΥΤΟ)	ΓΑΡΔΕΝΙΑ ΔΕΝΤΡΟ (ΟΧΙ ΦΥΤΟ)		1	25	19	Moesis	0	25		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
645	44	\N	ΓΙΑΣΕΜΙ ΜΠΛΕ	ΓΙΑΣΕΜΙ ΜΠΛΕ		1	4	19	In-house Production	0	4		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
646	44	\N	ΟΡΤΑΝΣΙΕΣ	ΟΡΤΑΝΣΙΕΣ		4	15	19	Shaelos	0	60		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
648	44	\N	ΓΟΥΙΣΤΕΡΙΕΣ	ΓΟΥΙΣΤΕΡΙΕΣ		2	30	19	Other	0	60		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
672	47	\N	Συκαμιά καλλωπιστική πλατύφυλλη άκαρπη	Συκαμιά καλλωπιστική πλατύφυλλη άκαρπη	1.5m/7L	37	18	19	Chrysovalantis 	12	666	1,5 m	9	0	PENDING	NOT_ORDERED	\N	\N	\N
683	48	1782	ALTERNANTHERA	ALTERNANTHERA	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
649	44	\N	Συκαμιά Άσπρη Κοντό			1	8	5	Chrysovalantis 	0	8		9	0	PENDING	NOT_ORDERED	\N	\N	\N
663	46	\N	Αγάπανθος	Agapanthus Africanus 		25	3.5	19	In-house Production	0	87.5	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
664	46	\N	Σέλουμ	Sellum		8	4.5	19	Panayiotou	3.5	36		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
665	46	\N	Washingtonian Palm 	Washingtonian Palm 		6	200	19	Nevada 	160	1200	2m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
660	46	\N	Λιγούστρο	Ligustrum 	130cm	43	20	19	Nevada 	14	860	150cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
661	46	\N	Date Palm 	Date Palm 	150cm	1	35	19	Plantech	25	35	2m	18	0	PENDING	NOT_ORDERED	\N	\N	\N
666	46	\N	Λεμονιά	Lemon Tree 	180cm	1	35	5	Plantech	25	35	2m	18	0	PENDING	NOT_ORDERED	\N	\N	\N
667	46	\N	Γιασεμί Γαλλικό	Jasmin 	2m	4	22	19	Plantech	16	88	2m	18	0	PENDING	NOT_ORDERED	\N	\N	\N
687	48	\N	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	80cm	11	15	19	In-house Production	0	165		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
688	48	530	CUPRESSUS SEMPERVIRENS TOTEM	CUPRESSUS SEMPERVIRENS TOTEM	1m	10	15	19	In-house Production	0	150		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
689	48	\N	DURANTA GOLD	DURANTA GOLD	2L	5	2.75	19	In-house Production	0	13.75		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
690	48	483	ELAEAGNUS PUNGENS	ELAEAGNUS PUNGENS	2L	3	3	19	In-house Production	0	9		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
691	48	\N	ELAEAGNUS X EBBINGEI	ELAEAGNUS X EBBINGEI	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
692	48	\N	LAVANDULA PINNATA	LAVANDULA PINNATA	2L	13	2	19	In-house Production	0	26		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
668	46	\N	Αρέκα	Areca Palm		3	150	19	Plantech	100	450	2m	18	0	PENDING	NOT_ORDERED	\N	\N	\N
670	15	\N	ΣΤΡΕΛΙΤΣΙΑ ΝΙΚΟΛΑΕ	STRELITZIA NICOLAI		8	15	19	In-house Production	10	120		2	0	PENDING	NOT_ORDERED	\N	\N	\N
671	47	\N	Tipuana Tipu Tree	Tipuana Tipu Tree	1m/2L	33	4.5	19	Moesis	3	148.5	1,5 m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
673	47	1742	Καλλιστήμονας	Καλλιστήμονας	1.5m/10L	12	15	19	In-house Production	0	180	1,5 m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
674	47	\N	Βραχυχύτων	Kurrajong Tree	1.5μ	10	12	19	Arocaria	8	120	1,5 m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
675	47	1724	Λασμαρί	Λασμαρί	20cm/2L	30	2	5	In-house Production	0	60	20 cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
678	47	1246	Μετροσίδερος	Metrosideros	25cm/5L	65	7	19	In-house Production	0	455	50 cm/5L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
680	47	\N	Λευκόφυλλο Πράσινο	Leucophyllum	13cm/2L	70	3	19	In-house Production	0	210	50 cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
693	48	\N	LIMONIUM SINUATUM	LIMONIUM 	2L	10	2.75	19	In-house Production	0	27.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
695	48	\N	PRUNUS CERASIFERA 'KRAUTER VESUVIUS'	PRUNUS CERASIFERA 'KRAUTER VESUVIUS'	6/8 2.5-3m	1	45	19	Arocaria	35	45		4	0	PENDING	NOT_ORDERED	\N	\N	\N
698	49	1782	Αλτερναθήρα	ALTERNANTHERA	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
696	48	\N	STIPA TENUISSIMA	STIPA TENUISSIMA		13	2.5	19	Arocaria	0	32.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
699	49	\N	ΛΕΜΟΝΙΑ	CITRUS LIMON	ΤΑΣΠΙΝ	1	15	5	Chrysovalantis 	11	15		9	0	PENDING	NOT_ORDERED	\N	\N	\N
701	49	\N	ΒΑΛΕΝΤΣΙΑ	CITRUS SINENSIS 'VALENCIA'	ΤΑΣΠΙΝ	1	15	5	Chrysovalantis 	11	15		9	0	PENDING	NOT_ORDERED	\N	\N	\N
720	50	\N	ΑΡΧΟΝΤΟΦΟΙΝΙΚΑΣ	ΑΡΧΟΝΤΟΦΟΙΝΙΚΑΣ	5L (SIZE B)	8	20	19	In-house Production	0	160	5L (SIZE B)	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
700	49	\N	ΚΛΕΜΕΝΤΙΝΗ	CITRUS MANDARINE	ΤΑΣΠΙΝ	1	15	5	Chrysovalantis 	11	15		9	0	PENDING	NOT_ORDERED	\N	\N	\N
702	49	546	Αριζόνικο	CUPRESSUS ARIZONICA	1,2m	5	13	19	Tsimouris	10	65		13	0	PENDING	NOT_ORDERED	\N	\N	\N
722	50	1798	ΣΤΡΕΛΙΤΣΙΑ NICOLAI	STRELITZIA NICOLAI	5L	8	10	19	In-house Production	0	80	5L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
723	50	\N	ΑΛΑΙΑΓΝΟΣ ΠΡΑΣΙΝΟΣ	ELEAGNOUS GREEN	2L	10	3.5	19	In-house Production	0	35	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
320	12	\N	ΤΟΥΡΠΑΤΣΙΑ	Tulbaghia violacea	2L	22	2.5	19	In-house Production	0	55	30cm	\N	16	PENDING	NOT_ORDERED	\N	\N	\N
323	12	\N	ΓΚΑΟΥΡΑ	Gaura lindtheimeri	2L	9	3	19	In-house Production	0	27	20/25cm	\N	19	PENDING	NOT_ORDERED	\N	\N	\N
324	12	\N	Ligustrum japonicum	Ligustrum japonicum	40cm	21	6.5	19	Arocaria	5	136.5	50/70cm	\N	20	PENDING	NOT_ORDERED	\N	\N	\N
322	12	483	ΕΛΑΙΑΓΝΟΣ ΠΡΑΣΙΝΟΣ	Elaeagnus pungens	2L	10	3.5	19	In-house Production	0	35	80/120cm	\N	18	PENDING	NOT_ORDERED	\N	\N	\N
329	12	\N	ΒΙΒΟΥΡΝΟ ΛΟΥΣΙΤΟΥΜ	Viburnum tinus 'Lucidum'	5L/50cm	17	8	19	In-house Production	0	136	80-120cm	2	25	PENDING	NOT_ORDERED	\N	\N	\N
304	12	\N	ΤΟΤΕΜ	Cupressus sempervirens 'Totem'	2m	4	45	19	Shaelos	35	180	200cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
306	12	\N	ΚΡΕΒΙΛΙΑ	Grevillea robusta	8/10-2,5-3m	1	70	19	Arocaria	55	70	200/250cm	\N	2	PENDING	NOT_ORDERED	\N	\N	\N
310	12	1262	ΑΡΤΥΜΑΤΙΑ	Schinus molle	8/10-2-2,5m	2	52	19	Shaelos	40	104	200/250cm	\N	6	PENDING	NOT_ORDERED	\N	\N	\N
311	12	\N	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolia	8/10-2-2,5m	2	45	19	Shaelos	35	90	200/250cm	\N	7	PENDING	NOT_ORDERED	\N	\N	\N
330	12	\N	ΒΟΥΚΑΜΒΗΛΙΑ	Bougainvillea glabra	200m	1	45	19	Shaelos	35	45	150-170cm	\N	26	PENDING	NOT_ORDERED	\N	\N	\N
333	12	1727	ΛΕΒΑΝΤΟΥΛΑ	Lavandula angustifolia		9	2	5	In-house Production	0	18	30cm	\N	29	PENDING	NOT_ORDERED	\N	\N	\N
335	12	\N	ΛΑΣΜΑΡΙ FOXTAIL	Rosmarinus officinalis 'Prostratus'		8	2	5	In-house Production	0	16	30cm	\N	31	PENDING	NOT_ORDERED	\N	\N	\N
709	49	\N	Λεβαντούλα	LAVANDULA PINNATA	2L	15	2	5	In-house Production	0	30		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
365	13	\N	Santolina chamaecyparissus	Santolina chamaecyparissus	15cm	53	3.5	19	In-house Production	0	185.5	30cm	\N	29	PENDING	NOT_ORDERED	\N	\N	\N
703	49	\N	SWANE'S GOLDEN	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	80cm	30	15	19	Moesis	10	450		5	0	PENDING	NOT_ORDERED	\N	\N	\N
299	11	\N	ΛΑΝΤΑΝΑ ΕΡΠΩΝ	Lantana montevidensis		5	3.5	19	Moesis	2.5	17.5	20cm	\N	32	PENDING	NOT_ORDERED	\N	\N	\N
704	49	530	TOTEM	CUPRESSUS SEMPERVIRENS TOTEM	1.1m	29	15	19	In-house Production	0	435		2	0	PENDING	NOT_ORDERED	\N	\N	\N
705	49	\N	DURANTA GOLD	DURANTA GOLD	2L	5	2.75	19	In-house Production	0	13.75		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
724	50	\N	ΚΑΡΙΣΣΑ ΑΓΚΑΘΙ	CARISSA	2L	9	3	19	In-house Production	0	27	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
301	11	1897	ΡΥΓΧΟΣΠΕΡΜΟ	Trachelospermum jasminoides	170cm	5	33	19	Shaelos	25	165	150-170cm	\N	34	PENDING	NOT_ORDERED	\N	\N	\N
706	49	483	Ελαίαγνος Δίχρωμος	ELAEAGNUS PUNGENS	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
303	11	\N	ΣΑΝΤΟΛΙΝΑ	Santolina chamaecyparissus	10cm	9	2	5	In-house Production	0	18	20cm	\N	36	PENDING	NOT_ORDERED	\N	\N	\N
302	11	\N	ΛΑΣΜΑΡΙ FOXTAIL	Rosmarinus officinalis 'Prostratus'	10cm	28	2	5	In-house Production	0	56	30cm	\N	35	PENDING	NOT_ORDERED	\N	\N	\N
372	14	\N	ΚΟΥΜ ΚΟΥΑΤ	FORTUNELLA MARGARITA		2	15	5	Chrysovalantis Nurseries	15	30	110cm	\N	6	PENDING	NOT_ORDERED	\N	\N	\N
367	14	\N	ΛΕΜΟΝΙΑ	CITRUS LIMON		1	55	5	Nevada Nurseries	40	55		\N	1	PENDING	NOT_ORDERED	\N	\N	\N
368	14	\N	ΚΛΕΜΕΝΤΙΝΗ	CITRUS MANDARINE		1	55	5	Nevada Nurseries	40	55		\N	2	PENDING	NOT_ORDERED	\N	\N	\N
681	47	526	Μερσηνια	Μερσηνια	25cm/5L	105	8	19	In-house Production	0	840	50 cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
682	47	1727	Λεβάντα	Λεβάντα	15cm/2L	30	2	5	In-house Production	0	60	20 cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
697	48	\N	TRADESCANTIA PALLIDA 'PURPLE HEART'	TRADESCANTIA PALLIDA 'PURPLE HEART'		8	2.5	19	Ginger	0	20		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
369	14	\N	SWANE'S GOLDEN	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'		1	15	19	Moesis	10	15	5L/80cm	\N	3	PENDING	NOT_ORDERED	\N	\N	\N
370	14	\N	ΣΕΒΙΛΛΗΣ	CUPRESSUS SEMPERVIRENS SEVILLE		1	10	19	In-house Production	0	10	5L/100cm	\N	4	PENDING	NOT_ORDERED	\N	\N	\N
371	14	\N	DURANTA GOLD	DURANTA GOLD		1	2.75	19	In-house Production	0	2.75	2L/25cm	\N	5	PENDING	NOT_ORDERED	\N	\N	\N
373	14	\N	JUNIPERUS HORIZONTALIS 'WILTONI' 'BLUE CHIP'	JUNIPERUS HORIZONTALIS 'WILTONI' 'BLUE CHIP'		1	3	19	In-house Production	0	3		\N	7	PENDING	NOT_ORDERED	\N	\N	\N
374	14	\N	ΕΛΙΑ ΣΤΕΜ	OLEA EUROPAEA STEM		3	33	5	Arocaria	25	99		\N	8	PENDING	NOT_ORDERED	\N	\N	\N
377	14	\N	STIPA TENUSSIMA	STIPA TENUSSIMA		7	2.5	19	In-house Production	0	17.5	2L	\N	11	PENDING	NOT_ORDERED	\N	\N	\N
710	49	480	Λιμονιουμ	LIMONIUM	2L	60	2.75	19	In-house Production	0	165		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
707	49	\N	Ελαίαγνος Πράσινος	ELAEAGNUS X EBBINGEI	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
708	49	\N	ΧΑΜΑΙΚΥΠΑΡΙΣΣΟ ΓΚΡΙΖΟ	JUNIPERUS HORIZONTALIS 'WILTONI' 'BLUE CHIP'	2L	2	3	19	In-house Production	0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
711	49	\N	Μετροσίδερο	METROSIDEROS EXCELSA	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
725	50	\N	ΑΛΑΙΑΓΝΟΣ ΔΙΧΡΩΜΟΣ	ELEAGNOUS YELLOW	2L	9	3.5	19	In-house Production	0	31.5	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
331	12	\N	ΜΑΡΓΑΡΙΤΑ ΚΑΖΑΝΙΑ	Gazania tomentosa		13	2.5	19	In-house Production	0	32.5	20cm	\N	27	PENDING	NOT_ORDERED	\N	\N	\N
727	50	\N	ΖΑΝΤΟΞΥΛΟ	ZANTOKSILO	2L	9	4	19	In-house Production	0	36	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
729	50	\N	ΡΙΓΑΝΗ	ORIGANO	2L	3	2	5	In-house Production	0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
730	50	\N	ΛΕΒΑΝΤΟΥΛΑ	LEVANDA PINATA	2L	3	2	5	In-house Production	0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
728	50	\N	ΛΑΣΜΑΡΙ	ROSEMARY	2L	3	2	5	In-house Production	0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
731	50	\N	ΛΕΒΑΝΤΑ	LEVANDA GRAY	2L	3	2	5	In-house Production	0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
336	12	\N	ΣΑΝΤΟΛΙΝΑ	Santolina chamaecyparissus		28	2	5	In-house Production	0	56	30cm	\N	32	PENDING	NOT_ORDERED	\N	\N	\N
733	50	\N	ΘΥΜΑΡΙ	ΘΥΜΑΡΙ	2L	3	2	5	In-house Production	0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
732	50	1271	ΒΑΣΙΛΙΚΟΣ	BASIL	2L	3	1.5	5	In-house Production	0	4.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
332	12	\N	Vinca minor	Vinca minor	4L	2	3.5	19	Moesis	2.5	7	20cm	\N	28	PENDING	NOT_ORDERED	\N	\N	\N
726	50	\N	ΤΟΥΡΑΝΤΑ GOLD	DURANDA GOLD	2L	13	3.5	19	In-house Production	0	45.5	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
379	14	1897	TRACHELOSPERMUM JASMINOIDES	TRACHELOSPERMUM JASMINOIDES		2	3.5	19	In-house Production	0	7	2L/1m	\N	13	PENDING	NOT_ORDERED	\N	\N	\N
381	15	\N	ARECASTRUM ROMANZOFFIANUM	ARECASTRUM ROMANZOFFIANUM		2	35	19	In-house Production	0	70	30L/1,7m	\N	1	PENDING	NOT_ORDERED	\N	\N	\N
385	15	\N	DIANELLA TASMANICA	DIANELLA TASMANICA		28	7	19	Arocaria	5	196	5L	\N	5	PENDING	NOT_ORDERED	\N	\N	\N
388	15	\N	PHILODENDRON SELLOUM	PHILODENDRON SELLOUM		6	5.5	19	Panayiotou	4.5	33	30cm	\N	8	PENDING	NOT_ORDERED	\N	\N	\N
389	15	533	PHOENIX ROEBELENII	PHOENIX ROEBELENII		4	20	19	In-house Production	0	80	15L/20cm κορμό	\N	9	PENDING	NOT_ORDERED	\N	\N	\N
390	15	\N	PLUMERIA ALBA	PLUMERIA ALBA		1	15	19	Moesis	10	15	10L/1,2m	\N	10	PENDING	NOT_ORDERED	\N	\N	\N
391	15	527	SCHEFFLERA ACTINOPHYLLA	SCHEFFLERA ACTINOPHYLLA		6	7	19	In-house Production	0	42	5L/1,1m	\N	11	PENDING	NOT_ORDERED	\N	\N	\N
393	15	535	STRELITZIA REGINAE	STRELITZIA REGINAE		4	12	19	In-house Production	0	48	10L/2pcs	\N	13	PENDING	NOT_ORDERED	\N	\N	\N
395	15	\N	WODYETIA BIFURCATA	WODYETIA BIFURCATA		1	175	19	Ginger	140	175	130cm	\N	15	PENDING	NOT_ORDERED	\N	\N	\N
736	50	\N	ΤΟΥΡΠΑΤΣΙΑ	TULBAGHIA	2L	2	2.5	19	In-house Production	0	5	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
378	14	\N	ΚΑΛΛΙΤΡΙΔΑ	TETRACLİNİS ARTICULATA		35	4	19	Tsimouris	3	140	70cm	13	12	PENDING	NOT_ORDERED	\N	\N	\N
386	15	\N	EUGENIA ETNA FIRE	EUGENIA ETNA FIRE		13	8	19	Ginger	6	104	4L	14	6	PENDING	NOT_ORDERED	\N	\N	\N
715	49	1828	Πιττόσπορο Νάνο	PITTOSPORUM TOBIRA NANA	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
500	20	\N	Φασκόμηλα	Φασκόμηλα		5	2	5	In-house Production	0	10		\N	11	PENDING	NOT_ORDERED	\N	\N	\N
716	49	\N	Κοκκινόφυλλη	PRUNUS CERASIFERA 'KRAUTER VESUVIUS'	6/8 2.5-3m	1	45	19	Arocaria	0	45		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
501	20	464	Δάφνη	Δάφνη		1	4.5	19	Moesis	2.5	4.5	2L	\N	12	PENDING	NOT_ORDERED	\N	\N	\N
288	11	\N	ΑΡΟΔΑΦΝΗ ΜΙΝΙ ΡΟΖ	Nerium oleander 'Petite pink'		5	3.5	19	Moesis	2.5	17.5	30cm	\N	21	PENDING	NOT_ORDERED	\N	\N	\N
712	49	\N	Μερσινιά μίνι	MYRTUS COMMUNIS 'COMPACTA'	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
292	11	500	ΠΟΛΥΚΑΛΑ	Polygala myrtifolia	2L	13	4	19	Moesis	3	52	80-100cm	\N	25	PENDING	NOT_ORDERED	\N	\N	\N
293	11	475	ΚΟΡΑΛΛΙ ΚΟΚΚΙΝΟ	Russelia equisetiformis		5	3.5	19	In-house Production	0	17.5	30cm	\N	26	PENDING	NOT_ORDERED	\N	\N	\N
737	50	\N	ΤΡΙΑΝΤΑΦΥΛΛΙΑ	ΤΡΙΑΝΤΑΦΥΛΛΙΑ	2L	2	8	19	In-house Production	0	16		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
734	50	\N	ΑΓΑΠΑΝΘΟΣ	AGAPANTHUS	2L	2	4	19	In-house Production	0	8	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
286	11	\N	ΓΚΑΟΥΡΑ	Gaura lindtheimeri		6	3	19	In-house Production	0	18	30cm	\N	19	PENDING	NOT_ORDERED	\N	\N	\N
394	15	\N	TRADESCANTIA PALLIDA 'PURPLE HEART'	TRADESCANTIA PALLIDA 'PURPLE HEART'	1L	14	2.5	19	Ginger	2	35	None	14	14	PENDING	NOT_ORDERED	\N	\N	\N
735	50	\N	ΦΕΣΤΟΥΚΑ	FESTUGA	2L	2	4	19	In-house Production	0	8	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
383	15	\N	ΚΛΕΜΕΝΤΙΝΗ	CITRUS MANDARINE	ΤΑΣΠΙΝ	1	15	5	Chrysovalantis 	12	15		\N	3	PENDING	NOT_ORDERED	\N	\N	\N
382	15	\N	ΛΕΜΟΝΙΑ	CITRUS LIMON	ΤΑΣΠΙΝ	1	15	5	Chrysovalantis 	12	15	1,5m	\N	2	PENDING	NOT_ORDERED	\N	\N	\N
384	15	\N	ΒΑΛΕΝΤΣΙΑ	CITRUS SINENSIS 'VALENCIA'	ΤΑΣΠΙΝ	1	15	5	Chrysovalantis 	12	15		\N	4	PENDING	NOT_ORDERED	\N	\N	\N
290	11	1836	Philodendron xanadu	Philodendron xanadu	2L	4	7.8	19	Panayiotou	6	31.2	30cm	6	23	PENDING	NOT_ORDERED	\N	\N	\N
296	11	\N	Asparagus  densiflorus 'Sprengeri'	Asparagus  densiflorus 'Sprengeri'	2L	24	4.5	19	Arocaria	3.25	108	20cm	4	29	PENDING	NOT_ORDERED	\N	\N	\N
380	15	\N	ARCHONTOPHOENIX CUNNINGHAMIANA	ARCHONTOPHOENIX CUNNINGHAMIANA		9	20	19	In-house Production	0	180	5L/1,7m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
502	20	\N	Yucca rostrata	Yucca rostrata		1	80	19	Shaelos	50	80		3	13	PENDING	NOT_ORDERED	\N	\N	\N
503	20	\N	Λεϋλάντι	Λεϋλάντι		3	8	19	In-house Production	0	24		\N	14	PENDING	NOT_ORDERED	\N	\N	\N
387	15	1823	MAGNOLIA GRANDIFLORA	MAGNOLIA GRANDIFLORA		1	52	19	Shaelos	65	52	1,5m	3	7	PENDING	NOT_ORDERED	\N	\N	\N
504	20	\N	Golden crest	Golden crest		2	8	19	In-house Production	0	16	5L	\N	15	PENDING	NOT_ORDERED	\N	\N	\N
508	20	\N	Ρομπελίνη	Ρομπελίνη		2	25	19	In-house Production	0	50		\N	16	PENDING	NOT_ORDERED	\N	\N	\N
509	20	\N	Cikkas λεπτόφυλλες	Cikkas λεπτόφυλλες		1	25	19	Panayiotou	0	25		\N	17	PENDING	NOT_ORDERED	\N	\N	\N
759	52	\N	ΠΕΝΙΣΕΤΟΥΜ ΠΡΑΣΙΝΟ	Pennisetum alopecuroides	15cm	2	3.5	19	In-house Production	0	7	2-3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
721	50	\N	ΒΙΒΟΥΡΝΟ ΛΟΥΣΙΤΟΥΜ	VIVORNO LUCIDUM	2L	11	3.5	19	In-house Production	0	38.5	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
758	52	\N	ΔΙΕΤΗΣ	Dietes grandiflora	30cm	12	3.5	19	In-house Production	0	42	2-3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
780	53	1823	Μακνόλια	Μακνόλια		1	80	19	Shaelos	52	80		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
781	53	\N	Ficus Amstel King	Ficus Amstel King		13	5	19	In-house Production	0	65		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
760	52	\N	Pennisetum alopecuroides 'Little bunny'	Pennisetum alopecuroides 'Little bunny'	50cm	26	1	19	In-house Production	0	26	2-3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
761	52	\N	Tulbaghia violacea	Tulbaghia violacea	30cm	35	2.5	19	In-house Production	0	87.5	2-3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
764	52	\N	Convolvulus sabatius	Convolvulus sabatius	20cm	14	3.5	19	Moesis	0	49	2/3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
773	52	\N	Rosmarinus officinalis 'Prostratus'	Rosmarinus officinalis 'Prostratus'	20cm	9	2	19	In-house Production	0	18	2-3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
767	52	\N	ΔΑΦΝΗ	Laurus nobilis	60cm	3	11	19	Arocaria	8	33	5lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
766	52	\N	ΓΚΑΟΥΡΑ	Gaura lindtheimeri	30cm	7	3	19	In-house Production	0	21	2/3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
770	52	\N	Pittosporum tobira 'Nana'	Pittosporum tobira 'Nana'	10cm	7	3.5	19	In-house Production	0	24.5	2/3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
762	52	\N	Duranta alba	Duranta alba	15cm/2L	6	3.5	19	Arocaria	2.5	21	5lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
768	52	\N	Ligustrum japonicum	Ligustrum japonicum	5L 	18	8	19	Arocaria	6	144	5lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
769	52	\N	Σχοινια	Pistacia lentiscus	30cm/5L	8	8	19	Shaelos	0	64	5lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
771	52	1897	Trachelospermum jasminoides	Trachelospermum jasminoides	150-170cm	3	16	19	Shaelos	12	48	5lit	3	0	PENDING	NOT_ORDERED	\N	\N	\N
772	52	\N	Perovskia artipilicifolia	Perovskia artipilicifolia	30cm	3	4	19	Arocaria	3	12	2-3lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
763	52	\N	ΚΑΡΙΣΣΑ ΝΑΝΑ	Carissa macrocarpa 'Green Carpet'	10cm	11	3	19	In-house Production	0	33	2/3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
774	52	1934	Santolina chamaecyparissus	Santolina chamaecyparissus	10cm	16	2	19	In-house Production	0	32	2-3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
765	52	1832	Ελαίαγνος Πράσινος	Elaeagnus pungens	45cm/5L	23	7	19	In-house Production	0	161	5lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
782	53	1971	Totem	Totem		3	15	19	In-house Production	0	45		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
783	53	1743	Μαστιχόδεντρο	Μαστιχόδεντρο		3	3.5	19	In-house Production	0	10.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
784	53	\N	Ευκάλυπτος Στρογγυλόφιλλος	Ευκάλυπτος Στρογγυλόφιλλος		3	7	19	In-house Production	0	21		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
785	53	\N	Πιττόσπορο Νάνα	Πιττόσπορο Νάνα		3	3	19	In-house Production	0	9		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
786	53	\N	Κάρυ	Κάρυ		2	2	5	In-house Production	0	4		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
787	53	\N	Λασμαρί Έρπων	Λασμαρί Έρπων		2	2	5	In-house Production	0	4		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
792	53	531	Συζύγιο	Συζύγιο		4	0	19	Other	0	0		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
791	53	532	Ευγενία Έτνα 	Ευγενία Έτνα 	170cm	3	28	19	Shaelos	16	84		3	0	PENDING	NOT_ORDERED	\N	\N	\N
789	53	550	Κοκκινόφυλλη	Κοκκινόφυλλη		3	18	19	Moesis	12	54		5	0	PENDING	NOT_ORDERED	\N	\N	\N
788	53	\N	Αλτερναθυρα	Αλτερναθυρα		16	3	19	In-house Production	0	48		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
790	53	\N	Ελαίαγνος Δίχρωμος	Ελαίαγνος Δίχρωμος		4	3.5	19	In-house Production	0	14		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
795	54	\N	ΜΕΡΛΙΝ	ΜΕΡΛΙΝ		1	18	19	Panayiotou	0	18	7Λ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
796	54	\N	ΚΛΕΜΕΝΤΙΝΗ	ΚΛΕΜΕΝΤΙΝΗ		2	18	19	Panayiotou	0	36	7Λ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
797	54	\N	ΑΡΑΚΑΠΑ	ΑΡΑΚΑΠΑ		1	18	19	Panayiotou	0	18	7Λ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
798	54	\N	ΛΑΝΤΑΝΑ ΠΟΡΤΟΚΑΛΙΑ	ΛΑΝΤΑΝΑ ΠΟΡΤΟΚΑΛΙΑ		15	4	19	Moesis	0	60	7Λ	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
799	54	\N	ΠΕΡΛΙΤΗΣ	ΠΕΡΛΙΤΗΣ		1	18	19	In-house Production	0	18		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
801	54	\N	ΜΑΡΟΥΛΙΑ 1*12			10	1.5	5	Ginger	0	15		14	0	PENDING	NOT_ORDERED	\N	\N	\N
800	54	\N	PEATOMOSS	PEATOMOSS		2	9.65	19	In-house Production	0	19.3	70L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
741	52	\N	Arecastrum romanzoffianum	Arecastrum romanzoffianum	200/250cm-20L	2	45	19	Moesis	30	90		5	0	PENDING	NOT_ORDERED	\N	\N	\N
746	52	548	Lagerstroemia indica	Lagerstroemia indica	2m/6-8 Girth	1	85	19	Shaelos	65	85	8-10 Girth	3	0	PENDING	NOT_ORDERED	\N	\N	\N
747	52	\N	Laurus nobilis tree (pyramidal)	Laurus nobilis tree (pyramidal)	150cm/8-10 Girth	3	100	19	Arocaria	75	300	10-12 Girth	4	0	PENDING	NOT_ORDERED	\N	\N	\N
749	52	\N	ΠΕΥΚΟΣ ΗΜΕΡΟΣ	Pinus pinea	250/300cm/12-14 Girth	1	185	19	Arocaria	125	185		4	0	PENDING	NOT_ORDERED	\N	\N	\N
802	55	1720	Αγιόκλημα	Αγιόκλημα		10	18	19	Arocaria	12	180	1,5-1,7m	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
803	54	\N	Συκαμιά Άκαρπη			1	40	19	Moesis	0	40		5	0	PENDING	NOT_ORDERED	\N	\N	\N
812	56	1953	Στεφανωτή	Στεφανωτή	2L	50	3.5	19	In-house Production	0	175		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
813	56	535	Στρελίτσια Reginae	Στρελίτσια Reginae	5L/1pc	50	6	19	In-house Production	0	300		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
814	56	509	Πιττόσπορο Νάνο	Πιττόσπορο Νάνο	2L	30	3.5	19	In-house Production	0	105		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
815	56	499	Πιττόσπορο Ορθοκλαδο	Πιττόσπορο Ορθοκλαδο	2L	30	3	19	In-house Production	0	90		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
816	56	487	Κάρισσα	Κάρισσα	2L	30	3	19	In-house Production	0	90		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
817	56	483	Αλαίαγνος	Αλαίαγνος	2L	30	3.5	19	In-house Production	0	105		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
818	56	\N	Αλαίαγνος Διχρωμος	Αλαίαγνος Διχρωμος	2L	30	3.5	19	In-house Production	0	105		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
819	56	472	Σχοινια 	Σχοινια 	2L	30	2.5	19	In-house Production	0	75		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
820	56	482	Τουράντα Gold	Τουράντα Gold	2L	30	3	19	In-house Production	0	90		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
821	56	474	Διέτης	Διέτης	2L	30	2.5	19	In-house Production	0	75		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
822	56	1790	Βιβούρνο Τίνους	Βιβούρνο Τίνους	2L	30	3.5	19	In-house Production	0	105		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
823	56	\N	Ευωνυμό	Ευωνυμό	2L	30	3	19	In-house Production	0	90		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
824	56	\N	Βιτεξ	Βιτεξ	2L	30	3	19	In-house Production	0	90		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
804	56	1774	Θυμάρι	Θυμάρι	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
805	56	\N	Κάρυ	Κάρυ	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
806	56	\N	Λασμαρί foxtail	Λασμαρί foxtail	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
807	56	\N	Λεβάντα Les Bleus Thierry	Λεβάντα Les Bleus Thierry	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
808	56	1727	Λεβάντα Κυπριακή	Λεβάντα Κυπριακή	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
809	56	\N	Μελισσόχορτο	Μελισσόχορτο	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
810	56	1763	Ρίγανη	Ρίγανη	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
811	56	1776	Σαντολίνα	Σαντολίνα	2L	50	2	5	In-house Production	0	100		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
825	57	\N	Πιττοσπορο ορθοκλαδο	Πιττοσπορο ορθοκλαδο	2L	4	3	19	In-house Production	0	12		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
826	57	\N	golden swanes 	golden swanes 	5L	2	8	19	In-house Production	0	16		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
827	57	1971	totem 	totem 	10L	3	15	19	In-house Production	0	45		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
828	57	\N	Strelitzia Reginae 	Strelitzia Reginae 	10L/2pcs	2	12	19	In-house Production	0	24		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
829	57	\N	Strelitzia Nicolae 	Strelitzia Nicolae 	5L	2	8	19	In-house Production	0	16		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
830	57	\N	agapanthus 	agapanthus 	2L	2	3.5	19	In-house Production	0	7		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
831	57	\N	arcontophoinix cumm 	arcontophoinix cumm 		2	25	19	In-house Production	0	50		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
832	57	\N	archontophoinix 	archontophoinix 		4	20	19	In-house Production	0	80		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
833	57	\N	royal palm 	royal palm 		20	0	19	In-house Production	0	0		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
834	57	1753	θουγια 	θουγια 		5	8	19	In-house Production	0	40		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
835	57	1741	αρτυματια	αρτυματια	10L	3	12	19	In-house Production	0	36		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
836	57	\N	λεμόνια 	λεμόνια 		2	15	5	In-house Production	0	30		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
837	57	\N	Σιεφλερα 	Σιεφλερα Αχτινοφυλλη	5L	2	8	19	In-house Production	0	16		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
838	57	\N	κλεμεντινη 	κλεμεντινη 		1	15	5	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
839	57	526	μερσηνια 	μερσηνια 		3	8	19	In-house Production	0	24	5L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
840	57	\N	Σιεφλερα δίχρωμη	Σιεφλερα δίχρωμη		3	0	19	In-house Production	0	0		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
846	58	1971	ΚΥΠΑΡΙΣΣΙ	Cupressus sempervirens	1.50Μ/9	31	12	19	Tsimouris	8	372	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
860	58	1969	ΓΚΑΟΥΡΑ	Gaura	15cm/2L	28	3	19	In-house Production	0	84	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
855	58	\N	ΤΕΚΟΜΑΡΙΑ ΠΟΡΤΟΚΑΛΙΑ	Tecomaria capensis	10cm/2L	22	3.5	19	In-house Production	0	77	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
853	58	487	ΚΑΡΙΣΣΑ	Carissa macrocarpa	20cm/2L	40	4	19	In-house Production	0	160	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
859	58	464	ΑΡΟΔΑΦΝΗ	Nerium oleander	80cm/2L	30	3	19	In-house Production	0	90	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
862	58	\N	ΛΕΒΑΝΤΑ	Lavender angustifolia	25cm/2L	48	2	5	In-house Production	0	96	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
850	58	\N	ΜΑΚΝΟΛΙΑ	Magnolia grandiflora (new)	1.5M/4-6 Girth	2	90	19	Shaelos	65	180	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	3	0	PENDING	NOT_ORDERED	\N	\N	\N
863	58	1725	ΛΑΣΜΑΡΙ ΟΡΘΟΚΛΑΔΟ	Rosmarinus officinalis	30cm/2L	92	2	5	In-house Production	0	184	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
858	58	\N	ΠΙΤΤΟΣΠΟΡΟ ΝΑΝΑ	Pittosporum tobira nana	20cm/2L	18	3.5	19	In-house Production	0	63	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
856	58	\N	ΔΙΕΤΗΣ	Dietes grandiflora	20cm/2L	15	3	19	In-house Production	0	45	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
852	58	\N	ΠΕΝΙΣΕΤΟΥΜ ΚΟΚΚΙΝΟ	Pennisetum setaceum red	10CM	26	3.5	19	In-house Production	0	91	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
857	58	1828	ΠΙΤΤΟΣΠΟΡΟ	Pittosporum tobira	50cm/2L	39	3.5	19	In-house Production	0	136.5	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
861	58	1782	ΑΛΤΕΡΝΑΘΗΡΑ	Alternanthera	20cm/2L	48	3.5	19	In-house Production	0	168	0,25m/2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
843	58	1262	ΑΡΤΥΜΑΤΙΑ	Schinus molle	1,50m/15L-(3-4 Girth)	9	20	19	In-house Production	0	180	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
841	58	\N	ΠΕΥΚΟΣ ΑΓΡΙΟΣ	Pinus halepensis	1,5m/15L(3-4 Girth)	4	20	19	In-house Production	0	80	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
879	62	\N	Θούγια	Θούγια	5L	20	8	19	In-house Production	0	160		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
888	62	519	Ρυγχόσπερμο	Ρυγχόσπερμο		25	3.5	19	In-house Production	0	87.5	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
889	12	\N	Peatmoss 250L		250L	5	25	19		19	125		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
866	58	\N	Δεντρο του Ιούδα	Cercis	2-2.5m/2-4Girth	1	60	19	Nevada 	35	60	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	12	0	PENDING	NOT_ORDERED	\N	\N	\N
864	58	\N	Κοκκινόφυλλη	Prunus negra	160cm/1-2 Girth/25L	1	35	19	Chrysovalantis 	45	35	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	9	0	PENDING	NOT_ORDERED	\N	\N	\N
870	58	\N	Κισσός	Hedera helix	1.2-1.4m/2L	27	8	19	Nevada 	0	216	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	12	0	PENDING	NOT_ORDERED	\N	\N	\N
869	58	\N	Plumeria rubra	Plumeria rubra	50cm/3L	3	8	19	Panayiotou	5	24	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	6	0	PENDING	NOT_ORDERED	\N	\N	\N
867	58	\N	Jacaranda	Jacaranda	1-2Girth/1.5-1.7m	2	30	19	Panayiotou	10	60	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	6	0	PENDING	NOT_ORDERED	\N	\N	\N
876	62	\N	Archontophoenix 	Archontophoenix 		50	10	19	In-house Production	0	500		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
865	58	\N	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolius	2-2.5m/4-6Girth	8	35	19	Nevada 	20	280	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	12	0	PENDING	NOT_ORDERED	\N	\N	\N
776	53	1725	Λασμαρί Ορθόκλαδο	Λασμαρί Ορθόκλαδο	2L	1	2	5	In-house Production	0	2		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
778	53	\N	Μερσηνιά	Μερσηνιά	2L	5	3	19	In-house Production	0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
877	62	535	Στρελίτσια Reginae	Στρελίτσια Reginae		50	6	19	In-house Production	0	300	5L/1pc	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
878	62	489	Κάρισσα Νάνα	Κάρισσα Νάνα		30	3	19	In-house Production	0	90	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
880	62	1774	Θυμάρι	Θυμάρι		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
881	62	\N	Κάρυ	Κάρυ		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
882	62	\N	Λασμαρί foxtail	Λασμαρί foxtail		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
883	62	\N	Λεβάντα Les Bleus Thierry	Λεβάντα Les Bleus Thierry		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
884	62	1727	Λεβάντα Κυπριακή	Λεβάντα Κυπριακή		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
885	62	1728	Λεβαντούλα	Λεβαντούλα		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
886	62	1763	Ρίγανη	Ρίγανη		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
887	62	1776	Σαντολίνα	Σαντολίνα		30	2	19	In-house Production	0	60	2L	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
896	65	\N	Arecastrum  romanzoffianum	Arecastrum  romanzoffianum	30L	2	45	19	Moesis	35	90		5	0	PENDING	NOT_ORDERED	\N	\N	\N
899	65	\N	Μουριά Άκαρπη	Morus nigra	20L/150cm-170cm	1	45	19	Chrysovalantis 	30	45	8-10Girth	9	0	PENDING	NOT_ORDERED	\N	\N	\N
897	65	\N	Cupressus  sempervirens 'Totem'	Cupressus  sempervirens 'Totem'	170cm	2	45	19	Shaelos	35	90	8-10Girth	3	0	PENDING	NOT_ORDERED	\N	\N	\N
904	65	\N	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolia	2/4-6Girth	1	26	19	Nevada 	20	26		12	0	PENDING	NOT_ORDERED	\N	\N	\N
902	65	\N	Prunus cerasifera NIgra	Prunus cerasifera NIgra	180cm/6-8 Girth	1	60	19	Arocaria	45	60	8-10Girth	4	0	PENDING	NOT_ORDERED	\N	\N	\N
900	65	552	Olea europaea	Olea europaea	170cm/50L	3	250	5	Arocaria	175	750	50lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
903	65	527	Schefflera actinophylla	Schefflera actinophylla	20L/150cm-170cm	1	65	19	In-house Production	0	65		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
905	65	534	Strelitzia nicolai	Strelitzia nicolai	130cm	4	15	19	Other	10	60		11	0	PENDING	NOT_ORDERED	\N	\N	\N
906	65	\N	Dianella tasmanica	Dianella tasmanica	5L	9	7	19	Arocaria	5	63	2lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
901	65	533	Phoenix roebelenii	Phoenix roebelenii	20L/30cm trunk	2	35	19	In-house Production	0	70		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
907	65	1927	Dietes bicolor	Dietes bicolor	2L	6	3	19	In-house Production	0	18	2lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
908	65	\N	Pennisetum alopecuroides	Pennisetum alopecuroides	2L	2	3	19	In-house Production	0	6	2lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
909	65	\N	Pennisetum setaceum 'Rubrum'	Pennisetum setaceum 'Rubrum'	2L	2	3	19	In-house Production	0	6	2lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
910	65	\N	Stipa tenuissima	Stipa tenuissima	2L	9	2.5	19	In-house Production	0	22.5	2lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
911	65	\N	Tulbaghia violacea	Tulbaghia violacea	2L	5	2.5	19	In-house Production	0	12.5	2lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
912	65	\N	Agave attenuata	Agave attenuata	5L	4	15	19	In-house Production	0	60	5/7lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
924	12	\N	Μερσινιά μίνι		2L	4	3	19		0	12		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
913	65	525	Elaeagnus pungens	Elaeagnus pungens	5L	2	7	19	In-house Production	0	14	5lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
925	58	\N	Γιαννης		5L/80cm	1	6	19		0	6		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
926	58	\N	Γιαννης		7L/130cm	1	15	19	Arocaria	10	15		4	0	PENDING	NOT_ORDERED	\N	\N	\N
914	65	\N	Ligustrum japonicum	Ligustrum japonicum	5L	10	7	19	Arocaria	5	70	5lit	4	0	PENDING	NOT_ORDERED	\N	\N	\N
927	66	\N	ΠΕΝΙΣΕΤΟΥΜ ΠΡΑΣΙΝΟ			13	1.75	19		0	22.75		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
915	65	1836	Philodendron xanadu	Philodendron xanadu	2L	5	5	19	Panayiotou	3.5	25	5-7lit	6	0	PENDING	NOT_ORDERED	\N	\N	\N
916	65	\N	Pittosporum tobira 'Nana'	Pittosporum tobira 'Nana'	2L	6	3	19	In-house Production	0	18	2/3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
917	65	\N	Senecio mandraliscae	Senecio mandraliscae	1L	8	2.5	19	Other	0	20	2/3lit	11	0	PENDING	NOT_ORDERED	\N	\N	\N
918	65	\N	Strelitzia reginaea	Strelitzia reginaea	5L/1pc	4	6	19	In-house Production	0	24	5-7lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
919	65	\N	Teucrium fruticans	Teucrium fruticans	2L	2	2.5	19	In-house Production	0	5	3-5lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
920	65	\N	Viburnum Tinus 'Lucidum'	Viburnum Tinus 'Lucidum'	5L	14	7	19	In-house Production	0	98	5/7lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
921	65	1897	Trachelospermum jasminoides	Trachelospermum jasminoides	2L/50cm	5	3.5	19	In-house Production	0	17.5	5lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
922	65	1727	Lavandula angustifolia	Lavandula angustifolia	2L	4	2	5	In-house Production	0	8	2/3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
923	65	\N	Rosmarinus officinalis 'Prostratus'	Rosmarinus officinalis 'Prostratus'	2L	6	2	5	In-house Production	0	12	2/3lit	\N	0	PENDING	NOT_ORDERED	\N	\N	\N
929	66	\N	ΚΑΡΙΣΣΑ ΝΑΝΑ		2L	26	2.5	19		0	65		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
930	66	\N	Αροδάφνη Μίνη Ροζ		2L	20	2	19		0	40		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
931	66	\N	ΔΙΕΤΗΣ		2L	6	2.5	19		0	15		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
932	66	\N	Οστεόσπερμο Άσπρη		2L	6	1.75	19		0	10.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
928	66	\N	ΛΕΒΑΝΤΟΥΛΑ		2L	23	1.5	5		0	34.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
933	67	\N	ΚΑΡΙΣΣΑ ΝΑΝΑ		2L	21	2.5	19		0	52.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
934	67	\N	ΛΑΣΜΑΡΙ		2L	65	1.5	5		0	97.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
935	67	\N	Τευκριο		2L	24	2.5	19		0	60		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
936	67	\N	Οστεόσπερμο Άσπρη		2L	38	1.75	19		0	66.5		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
937	67	\N	ΒΙΒΟΥΡΝΟ ΛΟΥΣΙΤΟΥΜ		2L	10	2.5	19		0	25		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
938	67	\N	Λιμονιουμ		2L	15	2	19		0	30		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
939	67	\N	ΔΙΕΤΗΣ			14	2.5	19		0	35		\N	0	PENDING	NOT_ORDERED	\N	\N	\N
\.


--
-- Data for Name: supplier; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.supplier (id, name, contact_person, email, phone, address, notes, is_inhouse, created_at, updated_at) FROM stdin;
2	In-house Production	\N	\N	\N	\N	Plants grown in our own nursery	t	2025-04-02 20:18:39.861893	2025-04-02 20:18:39.861893
3	Shaelos	\N	\N	\N	\N	External supplier found in test01.xlsx	f	2025-04-02 20:18:58.181613	2025-04-02 20:18:58.181613
4	Arocaria	\N	\N	\N	\N	External supplier found in test01.xlsx	f	2025-04-02 20:18:58.181613	2025-04-02 20:18:58.181613
1	H&G	Λινος				Generic category for miscellaneous external suppliers	f	2025-04-02 20:18:39.861893	2025-04-03 19:07:06.480883
5	Moesis						f	2025-04-03 19:09:25.922752	2025-04-04 18:23:59.674577
6	Panayiotou	Ntinos					f	2025-04-04 20:13:21.68092	2025-04-04 20:13:21.680927
7	Chrymaris	Gavriilis					f	2025-04-04 20:14:54.692584	2025-04-04 20:14:54.69259
8	Theodorides	Neofytos					f	2025-04-04 20:15:51.734183	2025-04-04 20:15:51.734189
10	Lakkotripi						f	2025-04-04 20:44:01.000459	2025-04-04 20:44:01.000465
11	Other	\N	\N	\N	\N	\N	f	2025-04-05 11:31:46.182149	2025-04-05 11:31:46.182165
13	Tsimouris	Pampos					f	2025-04-05 19:24:15.592361	2025-04-05 19:24:15.592364
9	Chrysovalantis 	Roulla					f	2025-04-04 20:43:37.473695	2025-04-05 20:55:06.995097
12	Nevada 	Polys					f	2025-04-05 19:23:56.328279	2025-04-05 20:55:31.004359
14	Ginger	Pavlos					f	2025-04-05 20:55:59.917123	2025-04-05 20:55:59.91713
15	Synthesis	Αντώνης	\N	\N	\N	\N	f	2025-04-09 14:36:17.371435	2025-04-09 14:36:17.371439
16	Chrysovalantis Nurseries	\N	\N	\N	\N	Automatically created from quotation	f	2025-04-09 15:14:03.565242	2025-04-09 15:14:03.565248
17	Nevada Nurseries	\N	\N	\N	\N	Automatically created from quotation	f	2025-04-17 13:46:53.20288	2025-04-17 13:46:53.202885
18	Plantech	Χάρης	\N	\N	Πάφος	\N	f	2025-04-30 12:30:28.891515	2025-04-30 12:30:28.89152
\.


--
-- Data for Name: supplier_product; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.supplier_product (id, supplier_id, product_name, scientific_name, height, pot_size, price, cost_price, last_detected, notes, created_at, updated_at, flagged_duplicate) FROM stdin;
72	2	Calamagrostis acutiflora	Calamagrostis acutiflora	50cm		0.01	0	2025-04-04 15:48:36.18741	\N	2025-04-04 15:48:36.188046	2025-04-04 15:48:36.188048	f
80	2	ΑΛΟΚΑΣΙΑ	Alocasia odora	50-80cm		0.01	0	2025-04-04 15:48:38.838318	\N	2025-04-04 15:48:38.838939	2025-04-04 15:48:38.83894	f
91	2	ΠΟΛΥΓΑΛΑ	Polygala myrtifolia	80-100cm		0.01	0	2025-04-04 15:48:42.444248	\N	2025-04-04 15:48:42.445007	2025-04-04 15:48:42.445009	f
97	2	ΚΑΖΑΝΙΑ	Gazania tomentosa	20cm		2.5	0	2025-04-04 15:48:45.270054	\N	2025-04-04 15:48:45.270704	2025-04-04 15:48:45.270706	f
103	2	ΠΟΛΥΓΑΛΑ	Polygala myrtifolia	80-100cm	20cm	3.5	0	2025-04-05 10:10:38.674629	\N	2025-04-05 10:10:38.67649	2025-04-05 10:10:38.676493	f
73	2	ΔΙΑΝΕΛΛΑ	Dianella tasmanica	30cm		7	5	2025-04-05 10:16:48.858288	\N	2025-04-04 15:48:36.510684	2025-04-05 10:16:48.859468	f
105	4	ΔΙΑΝΕΛΛΑ	Dianella tasmanica	30cm		7	5	2025-04-05 10:17:41.944034	\N	2025-04-05 10:17:41.944739	2025-04-05 10:17:41.944741	f
86	2	ΜΠΑΝΑΝΙΑ	Musa acuminata	150/200cm		0.01	0	2025-04-05 10:18:55.235086	\N	2025-04-04 15:48:40.825214	2025-04-05 10:18:55.236113	f
115	11	Philodendron selloum	Philodendron selloum	50cm		0	0	2025-04-05 15:42:34.276529	\N	2025-04-05 11:31:51.398211	2025-04-05 15:42:34.277277	f
68	1	ΔΡΑΚΑΙΝΑ	Dracaena  marginata	120/150cm	3pcs	50	40	2025-04-05 11:31:44.940763	\N	2025-04-04 15:48:34.891717	2025-04-05 11:31:44.941358	f
69	2	ΝΟΛΙΝΑ	Nolina recurvata	80/100cm	1m	60	0	2025-04-05 11:31:45.259321	None	2025-04-04 15:48:35.215352	2025-04-05 11:31:45.259896	f
70	4	ΕΛΙΑ ΣΤΕΜ	Olea europaea	150cm	1,5m	57	45	2025-04-05 11:31:45.578388	\N	2025-04-04 15:48:35.537202	2025-04-05 11:31:45.578961	f
71	2	ΑΓΑΠΑΝΘΟΣ	Agapanthus africanus	30cm	15cm	3.5	0	2025-04-05 11:31:45.909296	\N	2025-04-04 15:48:35.866138	2025-04-05 11:31:45.909854	f
74	2	ΔΙΕΤΗΣ	Dietes bicolor	40cm		3.5	0	2025-04-05 11:31:46.925127	\N	2025-04-04 15:48:36.835645	2025-04-05 11:31:46.925703	f
75	2	ΦΕΣΤΟΥΚΑ	Festuca glauca	20cm		3.5	0	2025-04-05 11:31:47.242298	\N	2025-04-04 15:48:37.172942	2025-04-05 11:31:47.242842	f
76	2	ΠΕΝΙΣΕΤΟΥΜ ΠΡΑΣΙΝΟ	Pennisetum alopecuroides	2-3lit		3.5	0	2025-05-15 13:13:19.8293	\N	2025-04-04 15:48:37.49763	2025-05-15 13:13:19.829815	f
83	2	ΚΑΡΙΣΣΑ ΝΑΝΑ	Carissa macrocarpa 'Green Carpet'	2/3lit	2L/10cm	3	0	2025-05-15 13:17:37.068131	\N	2025-04-04 15:48:39.81219	2025-05-15 13:17:37.068659	f
109	11	Alocasia odora	Alocasia odora	50-80cm		0	0	2025-04-05 11:31:48.849704	\N	2025-04-05 11:31:48.850338	2025-04-05 11:31:48.850341	f
110	7	ΑΛΟΗ ΒΕΡΑ	Aloe vera	30cm	5L	7	5	2025-04-05 11:31:49.168023	\N	2025-04-05 11:31:49.168668	2025-04-05 11:31:49.16867	f
111	11	Bulbine frutescens	Bulbine frutescens	30cm		0	0	2025-04-05 11:31:49.485271	\N	2025-04-05 11:31:49.485935	2025-04-05 11:31:49.485937	f
112	6	ΕΡΩΤΑΣ	Euphorbia milii	50cm		6	4.5	2025-04-05 11:31:50.120521	\N	2025-04-05 11:31:50.121223	2025-04-05 11:31:50.121226	f
113	11	ΜΠΑΝΑΝΙΑ	Musa acuminata	150/200cm		0	0	2025-04-05 11:31:50.759927	\N	2025-04-05 11:31:50.76058	2025-04-05 11:31:50.760582	f
114	5	ΑΡΟΔΑΦΝΗ ΜΙΝΙ ΡΟΖ	Nerium oleander 'Petite pink'	30cm		3.5	2.5	2025-04-05 11:31:51.080354	\N	2025-04-05 11:31:51.081064	2025-04-05 11:31:51.081067	f
116	1	Philodendron xanadu	Philodendron xanadu	30cm	2L	7.8	6	2025-04-05 11:31:51.715163	\N	2025-04-05 11:31:51.71586	2025-04-05 11:31:51.715863	f
117	1	ΠΙΤΤΟΣΠΟΡΟ 'Nana'	Pittosporum tobira 'Nana'	30cm	5L	15	10	2025-04-05 11:31:52.032396	\N	2025-04-05 11:31:52.033071	2025-04-05 11:31:52.033073	f
118	5	ΠΟΛΥΚΑΛΑ	Polygala myrtifolia	80-100cm	2L	4	3	2025-04-05 11:31:52.349388	\N	2025-04-05 11:31:52.350022	2025-04-05 11:31:52.350025	f
92	2	ΚΟΡΑΛΛΙ ΚΟΚΚΙΝΟ	Russelia equisetiformis	30cm		3.5	0	2025-04-05 11:31:52.668461	\N	2025-04-04 15:48:42.772287	2025-04-05 11:31:52.669022	f
93	4	Senecio mandraliscae	Senecio mandraliscae		2L	6.5	5	2025-04-05 11:31:52.986665	\N	2025-04-04 15:48:43.096614	2025-04-05 11:31:52.987169	f
119	1	Westringia fruticosa	Westringia fruticosa	30cm	5L	10.5	8	2025-04-05 11:31:53.30795	\N	2025-04-05 11:31:53.308654	2025-04-05 11:31:53.308657	f
106	11	Calamagrostis acutiflora	Calamagrostis acutiflora	50cm		0	0	2025-04-05 11:51:42.365903	\N	2025-04-05 11:31:46.278119	2025-04-05 11:51:42.366476	f
123	5	ΛΑΝΤΑΝΑ	Lantana camara	30cm	17cm	4.5	2.5	2025-04-05 11:31:54.589252	\N	2025-04-05 11:31:54.590002	2025-04-05 18:28:37.125198	f
108	1	Pennisetum alopecuroides 'Little bunny'	Pennisetum alopecuroides 'Little bunny'	30cm	2L	5.5	4	2025-04-05 15:42:31.188383	\N	2025-04-05 11:31:47.891628	2025-04-08 18:18:51.83295	t
79	2	ΤΟΥΡΠΑΤΣΙΑ	Tulbaghia violacea	30cm		2.5	0	2025-04-15 17:22:54.650759	\N	2025-04-04 15:48:38.509507	2025-04-15 17:22:54.651302	f
120	1	Asparagus  densiflorus 'Sprengeri'	Asparagus  densiflorus 'Sprengeri'	20cm	2L	4.5	3.25	2025-04-15 17:30:29.845025	\N	2025-04-05 11:31:53.625935	2025-04-15 17:30:29.845541	f
101	2	ΛΑΣΜΑΡΙ ΟΡΘΟΚΛΑΔΟ'Prostratus'	Rosmarinus officinalis 'Prostratus'	30cm	10cm	2	0	2025-04-15 17:32:54.344389	\N	2025-04-04 15:48:46.59087	2025-04-15 17:32:54.344885	f
85	2	ΓΚΑΟΥΡΑ	Gaura lindtheimeri	0,25m/2L		3	0	2025-05-19 13:31:41.175848	\N	2025-04-04 15:48:40.463787	2025-05-19 13:31:41.176391	f
78	2	ΠΕΝΙΣΕΤΟΥΜ ΚΟΚΚΙΝΟ	Pennisetum setaceum 'Rubrum'	0,25m/2L		3.5	0	2025-05-19 14:13:04.307605	\N	2025-04-04 15:48:38.157764	2025-05-19 14:13:04.308247	f
107	4	ΔΙΑΝΕΛΛΑ	Dianella tasmanica	2lit	5L	7	5	2025-05-25 11:17:30.128356	\N	2025-04-05 11:31:46.607268	2025-05-25 11:17:30.12878	f
122	2	ΜΑΡΓΑΡΙΤΑ ΚΑΖΑΝΙΑ	Gazania tomentosa	20cm		2.5	0	2025-05-26 17:22:40.350607	\N	2025-04-05 11:31:54.272942	2025-05-26 17:22:40.352265	f
124	5	ΜΥΟΠΟΡΟ	Myoporum parvifolium	20cm	20cm	4	3	2025-04-05 11:31:54.951281	\N	2025-04-05 11:31:54.951952	2025-04-05 11:31:54.951955	f
126	2	ΛΑΣΜΑΡΙ	Rosmarinus officinalis 'Prostratus'	30cm	10cm	2	0	2025-04-05 11:31:55.590862	\N	2025-04-05 11:31:55.591552	2025-04-05 11:31:55.591555	f
127	3	ΤΟΤΕΜ	Cupressus sempervirens 'Totem'	200cm	2m	45	35	2025-04-05 11:51:39.585369	\N	2025-04-05 11:51:39.586127	2025-04-05 11:51:39.58613	f
128	4	ΦΕΪΖΟΓΙΑ	Feijoa sellowiana (Multi-stem)	120/150cm	stem 1,2m	20	15	2025-04-05 11:51:39.898429	\N	2025-04-05 11:51:39.899224	2025-04-05 11:51:39.899227	f
129	4	ΚΡΕΒΙΛΙΑ	Grevillea robusta	200/250cm	8/10-2,5-3m	70	55	2025-04-05 11:51:40.208058	\N	2025-04-05 11:51:40.208995	2025-04-05 11:51:40.208999	f
131	4	ΜΟΥΡΙΑ ΑΚΑΡΠΗ	Morus alba	200/250cm	8/10-2-2,5m	59	45	2025-04-05 11:51:40.823411	\N	2025-04-05 11:51:40.824156	2025-04-05 11:51:40.824159	f
132	4	ΚΟΚΚΙΝΟΦΥΛΛΗ	Prunus cerasifera 'Pissardii Nigra'	200/250cm	2-2,5	65	50	2025-04-05 11:51:41.132788	\N	2025-04-05 11:51:41.133472	2025-04-05 11:51:41.133475	f
134	3	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolia	200/250cm	8/10-2-2,5m	45	35	2025-04-05 11:51:41.74882	\N	2025-04-05 11:51:41.749527	2025-04-05 11:51:41.749541	f
135	2	ΑΓΑΠΑΝΘΟΣ	Agapanthus africanus	30cm	2L	3.5	0	2025-04-05 11:51:42.056838	\N	2025-04-05 11:51:42.05751	2025-04-05 11:51:42.057513	f
137	11	Miscanthus sinensis	Miscanthus sinensis	50cm		0	0	2025-04-05 11:51:42.989331	\N	2025-04-05 11:51:42.990016	2025-04-05 11:51:42.990019	f
142	2	ΚΑΡΙΣΣΑ ΝΑΝΑ	Carissa macrocarpa 'Green Carpet'		2L	3.5	0	2025-04-05 11:51:44.840684	\N	2025-04-05 11:51:44.841521	2025-04-05 11:51:44.841525	f
146	6	Metrosideros	Metrosideros excelsa	80/120cm	5L	15	10	2025-04-05 11:51:46.096093	\N	2025-04-05 11:51:46.096845	2025-04-05 11:51:46.096848	f
149	4	Senecio mandraliscae	Senecio mandraliscae	20cm	2L	6.5	5	2025-04-05 11:51:47.02804	\N	2025-04-05 11:51:47.028852	2025-04-05 11:51:47.028855	f
150	11	ΒΙΒΟΥΡΝΟ ΛΟΥΣΙΤΟΥΜ	Viburnum tinus 'Lucidum'	80-120cm	2L/20-30cm	3.5	13	2025-04-05 11:51:47.336227	\N	2025-04-05 11:51:47.337293	2025-04-05 11:51:47.337297	f
151	3	ΒΟΥΚΑΜΒΗΛΙΑ	Bougainvillea glabra	150-170cm	200m	45	35	2025-04-05 11:51:47.643615	\N	2025-04-05 11:51:47.644314	2025-04-05 11:51:47.644317	f
153	2	ΛΕΒΑΝΤΟΥΛΑ	Lavandula angustifolia	30cm		2	0	2025-04-05 11:51:48.568119	\N	2025-04-05 11:51:48.568834	2025-04-05 11:51:48.568837	f
155	2	ΛΑΣΜΑΡΙ FOXTAIL	Rosmarinus officinalis 'Prostratus'	30cm		2	0	2025-04-05 11:51:49.226696	\N	2025-04-05 11:51:49.227392	2025-04-05 11:51:49.227395	f
158	11	Brachychiton acerifolius	Brachychiton acerifolius	10-12 Girth/170/200cm		0	0	2025-04-05 15:42:27.806979	\N	2025-04-05 15:42:27.807916	2025-04-05 15:42:27.807919	f
162	11	Plumeria alba	Plumeria alba	170cm	1m/ροζ & κοκκινο	0	0	2025-04-05 15:42:29.176763	\N	2025-04-05 15:42:29.177616	2025-04-05 15:42:29.177618	f
163	11	Schefflera actinophylla	Schefflera actinophylla	8-10 Girth/150/170cm		0	0	2025-04-05 15:42:29.482214	\N	2025-04-05 15:42:29.483078	2025-04-05 15:42:29.483081	f
165	2	Cortaderia selloana	Cortaderia selloana	60cm		10	0	2025-04-05 15:42:30.140785	\N	2025-04-05 15:42:30.141638	2025-04-05 15:42:30.14164	f
170	11	Bougainvillea spectabilis	Bougainvillea spectabilis	80cm		0	0	2025-04-05 15:42:32.198516	\N	2025-04-05 15:42:32.199305	2025-04-05 15:42:32.199307	f
173	11	Fargesia robusta	Fargesia robusta	120/150cm		0	0	2025-04-05 15:42:33.269513	\N	2025-04-05 15:42:33.270354	2025-04-05 15:42:33.270358	f
175	2	Myrtus communis 'Nana'	Myrtus communis 'Nana'	30cm	5L	8	0	2025-04-05 15:42:33.972238	\N	2025-04-05 15:42:33.973078	2025-04-05 15:42:33.97308	f
177	6	Pittosporum tobira 'Nana'	Pittosporum tobira 'Nana'	30cm	5L	15	10	2025-04-05 15:42:34.982474	\N	2025-04-05 15:42:34.983339	2025-04-05 15:42:34.983342	f
147	2	ΜΕΡΣΗΝΙΑ ΨΙΝΤΡΟΦΥΛΛΗ	Myrtus communis 'Nana'	30cm	5L	10	0	2025-04-08 15:49:20.093714	\N	2025-04-05 11:51:46.404209	2025-04-08 15:49:20.094103	f
139	2	ΠΕΝΙΣΕΤΟΥΜ ΚΟΚΚΙΝΟ	Pennisetum setaceum 'Rubrum'	2lit	2L	3	0	2025-05-25 11:18:19.72385	\N	2025-04-05 11:51:43.917613	2025-05-25 11:18:19.724298	f
102	2	ΣΑΝΤΟΛΙΝΑ	Santolina chamaecyparissus	2-3lit	10cm	2	0	2025-05-15 13:17:47.904119	\N	2025-04-04 15:48:46.917183	2025-05-15 13:17:47.904938	f
164	3	Schinus terebinthifolia	Schinus terebinthifolia	10-12 Girth/200cm	2-2,5m/8-10G	54	35	2025-04-08 15:44:36.895567	\N	2025-04-05 15:42:29.83672	2025-04-08 15:44:36.895996	f
167	2	Pennisetum alopecuroides	Pennisetum alopecuroides	2lit	2L	3	0	2025-05-25 11:18:09.386659	\N	2025-04-05 15:42:30.840309	2025-05-25 11:18:09.387157	f
161	4	Olea europaea	Olea europaea	50lit		250	175	2025-05-25 11:12:32.811735	\N	2025-04-05 15:42:28.828558	2025-05-25 11:12:32.812245	f
138	2	ΠΕΝΙΣΕΤΟΥΜ ΠΡΑΣΙΝΟ	Pennisetum alopecuroides	50cm	2L	4.5	0	2025-04-08 15:45:33.785778	\N	2025-04-05 11:51:43.297722	2025-04-08 15:45:33.786195	f
157	5	Archontophoenix alexandrae	Archontophoenix alexandrae	150cm	120cm	108	60	2025-04-08 15:41:48.379637	\N	2025-04-05 15:42:27.498002	2025-04-08 15:41:48.380078	f
145	4	Ligustrum japonicum	Ligustrum japonicum	5lit	40cm	7	5	2025-05-25 11:20:27.387246	\N	2025-04-05 11:51:45.79011	2025-05-25 11:20:27.387962	f
174	2	Juniperus horizontalis	Juniperus horizontalis	50cm	2L	5	0	2025-04-08 15:48:47.315848	\N	2025-04-05 15:42:33.619072	2025-04-08 15:48:47.316395	f
143	2	ΕΛΑΙΑΓΝΟΣ ΠΡΑΣΙΝΟΣ	Elaeagnus pungens	5lit	5L	7	0	2025-05-25 11:19:00.642659	\N	2025-04-05 11:51:45.176936	2025-05-25 11:19:00.643108	f
148	6	ΠΙΤΤΟΣΠΟΡΟ 'Nana'	Pittosporum tobira 'Nana'	30cm	5L	18.5	10	2025-04-08 15:50:29.517964	\N	2025-04-05 11:51:46.721589	2025-04-08 15:50:29.518368	f
169	2	Tulbaghia violacea	Tulbaghia violacea	2lit	2L	2.5	0	2025-05-25 10:49:03.23216	\N	2025-04-05 15:42:31.891664	2025-05-25 10:49:03.233438	f
176	2	Pittosporum tobira	Pittosporum tobira	60/80cm	2L/50cm	3	0	2025-05-07 18:22:38.496397	\N	2025-04-05 15:42:34.628164	2025-05-07 18:22:38.496887	f
141	2	ΤΟΥΡΠΑΤΣΙΑ	Tulbaghia violacea	2lit	2L	2.5	0	2025-05-25 11:18:41.22699	\N	2025-04-05 11:51:44.533097	2025-05-25 11:18:41.227627	f
172	2	Αλαίαγνος ή Ελαίαγνος 5L	Elaeagnus Pungens	80/120cm	5L	10	0	2025-05-10 17:46:13.068176	\N	2025-04-05 15:42:32.965977	2025-05-10 17:46:13.069224	f
144	2	ΓΚΑΟΥΡΑ	Gaura lindtheimeri	20/25cm	2L	3	0	2025-05-10 17:46:29.80046	\N	2025-04-05 11:51:45.483006	2025-05-10 17:46:29.801045	f
156	2	ΣΑΝΤΟΛΙΝΑ	Santolina chamaecyparissus	30cm		2	0	2025-05-26 17:23:22.124442	\N	2025-04-05 11:51:49.53476	2025-05-26 17:23:22.125142	f
152	5	Vinca minor	Vinca minor	20cm	4L	3.5	2.5	2025-05-10 17:47:46.590235	\N	2025-04-05 11:51:48.262276	2025-05-10 17:47:46.59077	f
133	3	ΑΡΤΥΜΑΤΙΑ	Schinus molle	200/250cm	8/10-2-2,5m	52	40	2025-05-25 11:15:13.928075	\N	2025-04-05 11:51:41.442039	2025-05-25 11:15:13.92846	f
168	2	Stipa tenuissima	Stipa tenuissima	2lit	2L	2.5	0	2025-05-25 10:49:02.660622	\N	2025-04-05 15:42:31.538891	2025-05-25 10:49:02.661512	f
171	2	Carissa macrocarpa 'Green Carpet'	Carissa macrocarpa 'Green Carpet'	2/3lit	5L	3	0	2025-05-12 17:24:37.468248	\N	2025-04-05 15:42:32.554911	2025-05-12 17:24:37.46897	f
130	3	ΤΖΙΑΚΑΡΑΝΤΑ	Jacaranda mimosifolia	10-12 Girth	6/8-2-2,5m	45	35	2025-05-15 13:04:31.052636	\N	2025-04-05 11:51:40.516089	2025-05-15 13:04:31.053144	f
166	2	Dietes bicolor	Dietes bicolor	2lit	5L	3	0	2025-05-25 10:49:00.945476	\N	2025-04-05 15:42:30.490848	2025-05-25 10:49:00.946423	f
154	2	ΛΑΣΜΑΡΙ ΟΡΘΟΚΛΑΔΟ	Rosmarinus officinalis	0,25m/2L		2	0	2025-05-19 13:37:13.804416	\N	2025-04-05 11:51:48.88468	2025-05-19 13:37:13.804959	f
136	2	ΔΙΕΤΗΣ	Dietes bicolor	2lit	2L	3	0	2025-05-25 11:17:44.114288	\N	2025-04-05 11:51:42.681516	2025-05-25 11:17:44.114703	f
140	2	ΣΤΙΠΑ	Stipa tenuissima	2lit	2L	2.5	0	2025-05-25 11:18:31.78709	\N	2025-04-05 11:51:44.225036	2025-05-25 11:18:31.787509	f
184	5	ΚΥΚΑΣ ΡΕΒΟΛΟΥΤΑ	Cycas revoluta	100-120cm	25cm	65	65	2025-04-05 18:22:10.133234	\N	2025-04-05 18:22:10.133238	2025-04-05 18:22:10.133239	f
225	3	Brachychiton acerifolius	Brachychiton acerifolius	10-12 Girth/170/200cm	10-12 Girth/170/200cm	78	50	2025-04-08 15:42:18.869497	Created from quotation	2025-04-07 14:10:12.951216	2025-04-08 15:42:18.870042	f
159	6	Cycas revoluta	Cycas revoluta	60cm	12L	30	18	2025-04-08 15:42:38.22289	\N	2025-04-05 15:42:28.156632	2025-04-08 15:42:38.2235	f
160	4	Jacaranda mimosifolia	Jacaranda mimosifolia	10-12 Girth/200cm	3m/8-10G	90	55	2025-04-08 15:43:05.631806	\N	2025-04-05 15:42:28.518575	2025-04-08 15:43:05.632251	f
189	12	CITRUS LIMON	CITRUS LIMON			55	45	2025-04-05 19:27:00.617053	\N	2025-04-05 19:27:00.617945	2025-04-05 19:27:00.617948	f
190	12	CITRUS MANDARINE	CITRUS MANDARINE			55	45	2025-04-05 19:27:01.122176	\N	2025-04-05 19:27:01.122957	2025-04-05 19:27:01.122959	f
192	2	CUPRESSUS SEMPERVIRENS SEVILLE	CUPRESSUS SEMPERVIRENS SEVILLE	5L/100cm		10	0	2025-04-05 19:27:02.128043	\N	2025-04-05 19:27:02.12874	2025-04-05 19:27:02.128742	f
196	4	OLEA EUROPAEA STEM	OLEA EUROPAEA STEM			33	25	2025-04-05 19:27:04.137164	\N	2025-04-05 19:27:04.137895	2025-04-05 19:27:04.137897	f
197	5	PENNISETUM SETACEUM 'RUBRUM'	PENNISETUM SETACEUM 'RUBRUM'	2L		3.5	2.5	2025-04-05 19:27:04.638883	\N	2025-04-05 19:27:04.639666	2025-04-05 19:27:04.639668	f
200	13	TETRACLİNİS ARTICULATA	TETRACLİNİS ARTICULATA	1L/30cm		1.5	0.6	2025-04-05 19:27:06.149667	\N	2025-04-05 19:27:06.150484	2025-04-05 19:27:06.150487	f
202	12	ΛΕΜΟΝΙΑ	CITRUS LIMON			55	45	2025-04-05 19:28:08.060011	\N	2025-04-05 19:28:08.060701	2025-04-05 19:28:08.060703	f
203	12	ΚΛΕΜΕΝΤΙΝΗ	CITRUS MANDARINE			55	45	2025-04-05 19:28:37.604626	\N	2025-04-05 19:28:37.605489	2025-04-05 19:28:37.605492	f
204	2	ΣΕΒΙΛΛΗΣ	CUPRESSUS SEMPERVIRENS SEVILLE	5L/100cm		10	0	2025-04-05 19:30:55.357228	\N	2025-04-05 19:30:55.358015	2025-04-05 19:30:55.358017	f
188	5	ALTERNANTHERA	ALTERNANTHERA	2L/15cm		3	2.5	2025-04-05 19:39:17.948362	\N	2025-04-05 19:27:00.109137	2025-04-05 19:39:17.949459	f
191	5	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	5L/80cm		15	10	2025-04-09 11:47:58.33241	\N	2025-04-05 19:27:01.62587	2025-04-09 11:47:58.334747	f
207	4	ΕΛΙΑ ΣΤΕΜ	OLEA EUROPAEA STEM			33	25	2025-04-05 19:40:35.849694	\N	2025-04-05 19:36:18.147431	2025-04-05 19:40:35.850344	f
199	2	STIPA TENUSSIMA	STIPA TENUSSIMA	2L		2.5	0	2025-04-05 19:40:54.02173	\N	2025-04-05 19:27:05.648345	2025-04-05 19:40:54.022599	f
222	2	STRELITZIA REGINAE	STRELITZIA REGINAE	10L/2pcs		12	0	2025-04-15 11:24:49.590671	\N	2025-04-05 20:58:53.900213	2025-04-15 11:24:49.591617	f
181	2	Lavandula angustifolia	Lavandula angustifolia	2/3lit	1L/15cm	2	0	2025-05-25 11:24:15.950408	\N	2025-04-05 15:42:36.406346	2025-05-25 11:24:15.950826	f
212	9	CITRUS MANDARINE	CITRUS MANDARINE			15	0	2025-04-05 20:58:50.776611	\N	2025-04-05 20:58:50.777302	2025-04-05 20:58:50.777305	f
213	9	CITRUS SINENSIS 'VALENCIA'	CITRUS SINENSIS 'VALENCIA'			15	0	2025-04-05 20:58:51.08986	\N	2025-04-05 20:58:51.090614	2025-04-05 20:58:51.090617	f
219	5	PLUMERIA ALBA	PLUMERIA ALBA	10L/1,2m		15	10	2025-04-05 20:58:52.963343	\N	2025-04-05 20:58:52.964027	2025-04-05 20:58:52.96403	f
224	14	WODYETIA BIFURCATA	WODYETIA BIFURCATA	130cm		175	140	2025-04-05 20:58:54.516888	\N	2025-04-05 20:58:54.51755	2025-04-05 20:58:54.517552	f
223	4	TRADESCANTIA PALLIDA 'PURPLE HEART'	TRADESCANTIA PALLIDA 'PURPLE HEART'	None	1L	2.5	2	2025-04-17 13:36:36.795706	\N	2025-04-05 20:58:54.209856	2025-04-17 13:36:36.796271	f
195	2	JUNIPERUS HORIZONTALIS 'WILTONI' 'BLUE CHIP'	JUNIPERUS HORIZONTALIS 'WILTONI' 'BLUE CHIP'			3	0	2025-05-07 18:22:36.031369	\N	2025-04-05 19:27:03.635502	2025-05-07 18:22:36.031976	f
183	2	Santolina chamaecyparissus	Santolina chamaecyparissus	2-3lit	15cm	2	0	2025-05-12 17:24:42.963661	\N	2025-04-05 15:42:37.122041	2025-05-12 17:24:42.964297	f
215	4	EUGENIA ETNA FIRE	EUGENIA ETNA FIRE	4L		8	6	2025-04-05 21:00:44.897128	\N	2025-04-05 20:58:51.71824	2025-04-05 21:00:44.897733	f
210	2	ARECASTRUM ROMANZOFFIANUM	ARECASTRUM ROMANZOFFIANUM	30L/1,7m		1	0	2025-05-07 14:20:33.356648	\N	2025-04-05 20:58:50.143736	2025-05-07 14:20:33.357663	f
217	6	PHILODENDRON SELLOUM	PHILODENDRON SELLOUM	30cm		5.5	4.5	2025-04-05 21:01:26.661082	\N	2025-04-05 20:58:52.343426	2025-04-05 21:01:26.661641	f
221	2	STRELITZIA NICOLAI	STRELITZIA NICOLAI	5L		15	0	2025-05-25 10:48:59.783546	\N	2025-04-05 20:58:53.58339	2025-05-25 10:48:59.784066	f
211	9	CITRUS LIMON	CITRUS LIMON	8-10 Girth		1	11	2025-05-12 17:24:25.069739	\N	2025-04-05 20:58:50.452799	2025-05-12 17:24:25.070958	f
205	5	SWANE'S GOLDEN	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	5L/80cm		15	10	2025-05-07 18:30:16.357663	\N	2025-04-05 19:35:06.537647	2025-05-07 18:30:16.358154	f
216	12	MAGNOLIA GRANDIFLORA	MAGNOLIA GRANDIFLORA	1,5m		52	40	2025-04-17 13:38:34.733183	\N	2025-04-05 20:58:52.033629	2025-04-17 13:38:34.733805	f
230	2	Pampas grass	Cortaderia selloana	60cm		12.5	0	2025-04-08 15:44:55.204588	Created from quotation	2025-04-07 15:34:27.940975	2025-04-08 15:44:55.20499	f
201	2	TRACHELOSPERMUM JASMINOIDES	TRACHELOSPERMUM JASMINOIDES	5lit		3.5	0	2025-05-25 11:23:55.321708	\N	2025-04-05 19:27:06.652327	2025-05-25 11:23:55.322271	f
226	4	Plumeria alba	Plumeria alba	10-12 Girth	1.5m	60	45	2025-05-15 12:56:14.187244	Created from quotation	2025-04-07 14:27:56.728833	2025-05-15 12:56:14.188658	f
228	4	ΕΛΙΑ	Olea europaea	14-16 Girth/200cm		235	175	2025-05-15 13:06:18.440504	Created from quotation	2025-04-07 15:28:43.81015	2025-05-15 13:06:18.441431	f
229	2	ΣΙΕΦΛΕΡΑ ΑΚΤΙΝΟΦΥΛΛΗ	Schefflera actinophylla	8-10 Girth/150/170cm	120cm	10	0	2025-04-08 15:44:18.621768	Created from quotation	2025-04-07 15:32:25.500295	2025-04-08 15:44:18.622227	f
178	2	Viburnum tinus	Viburnum tinus	60/80cm	5L/50cm	12.5	0	2025-04-08 15:51:17.907529	\N	2025-04-05 15:42:35.331221	2025-04-08 15:51:17.907986	f
179	2	Gazania tomentosa	Gazania tomentosa	20cm	2L	3.5	0	2025-04-08 15:54:32.763629	\N	2025-04-05 15:42:35.699701	2025-04-08 15:54:32.76405	f
182	2	Rosmarinus officinalis	Rosmarinus officinalis	30cm	10cm	2.5	0	2025-04-08 15:55:37.173479	\N	2025-04-05 15:42:36.771738	2025-04-08 15:55:37.173898	f
220	2	SCHEFFLERA ACTINOPHYLLA	SCHEFFLERA ACTINOPHYLLA	5L/1,1m		65	0	2025-05-25 11:14:13.505887	\N	2025-04-05 20:58:53.274623	2025-05-25 11:14:13.506381	f
198	2	ROSMARINUS OFFICINALIS	ROSMARINUS OFFICINALIS	2L		2	0	2025-05-07 18:22:31.839855	\N	2025-04-05 19:27:05.145928	2025-05-07 18:22:31.840841	f
218	2	PHOENIX ROEBELENII	PHOENIX ROEBELENII	100cm		35	0	2025-05-26 15:38:22.766823	\N	2025-04-05 20:58:52.651319	2025-05-26 15:38:22.767476	f
208	13	ΚΑΛΛΙΤΡΙΔΑ	TETRACLİNİS ARTICULATA	70cm		4	3	2025-04-09 15:16:27.970696	\N	2025-04-05 19:36:51.302894	2025-04-09 15:16:27.972147	f
209	2	ARCHONTOPHOENIX CUNNINGHAMIANA	ARCHONTOPHOENIX CUNNINGHAMIANA	5L/1,7m		20	0	2025-04-17 13:33:02.687022	\N	2025-04-05 20:58:49.830199	2025-04-17 13:33:02.692836	f
231	4	ΣΤΙΠΑ	Stipa tenuissima	30cm	2L	3	2.5	2025-05-07 18:26:57.534076	Created from quotation	2025-04-07 17:13:54.07368	2025-05-07 18:26:57.534566	f
193	2	DURANTA GOLD	DURANTA GOLD	2L		2.75	0	2025-05-07 18:31:02.948906	\N	2025-04-05 19:27:02.63173	2025-05-07 18:31:02.949415	f
232	11	ΒΟΥΚΑΝΑΝΑ	Bougainvillea spectabilis	80cm		0.01	0	2025-04-07 17:14:34.677891	Created from quotation	2025-04-07 17:14:34.678604	2025-04-07 17:14:34.678606	f
248	11	Yucca rostrata	Yucca rostrata			0.01	0	2025-04-07 17:54:47.538821	Created from quotation	2025-04-07 17:54:47.539441	2025-04-07 17:54:47.539442	f
251	11	Μαστίχες	Μαστίχες			0.01	0	2025-04-07 17:54:49.285699	Created from quotation	2025-04-07 17:54:49.286399	2025-04-07 17:54:49.286401	f
252	11	Πυράκανθος	Πυράκανθος			0.01	0	2025-04-07 17:54:49.870761	Created from quotation	2025-04-07 17:54:49.871436	2025-04-07 17:54:49.871437	f
256	11	Πυξάρι	Πυξάρι			0.01	0	2025-04-07 17:54:52.229398	Created from quotation	2025-04-07 17:54:52.229942	2025-04-07 17:54:52.229943	f
234	2	Βιβούρνο (κοινό)	Βιβούρνο (κοινό)	2L		3.5	0	2025-04-07 18:07:08.610542	Created from quotation	2025-04-07 17:54:39.361893	2025-04-07 18:07:08.61153	f
235	2	Ελαίαγνους	Ελαίαγνους	2L		3.5	0	2025-04-07 18:07:09.214627	Created from quotation	2025-04-07 17:54:39.945577	2025-04-07 18:07:09.215077	f
236	2	Ελαίαγνους διχρωμο	Ελαίαγνους διχρωμο	2L		3.5	0	2025-04-07 18:07:09.845713	Created from quotation	2025-04-07 17:54:40.535269	2025-04-07 18:07:09.84614	f
237	2	Ευώνυμο διχρωμο	Ευώνυμο διχρωμο	2L		3.5	0	2025-04-07 18:07:10.450161	Created from quotation	2025-04-07 17:54:41.114096	2025-04-07 18:07:10.450678	f
238	4	Φωτίνιες	Φωτίνιες	4L		10	6	2025-04-07 18:07:11.109031	Created from quotation	2025-04-07 17:54:41.70199	2025-04-07 18:07:11.10948	f
239	4	Ευγένιες	Ευγένιες	4L		10	6	2025-04-07 18:07:11.703184	Created from quotation	2025-04-07 17:54:42.303127	2025-04-07 18:07:11.704138	f
240	2	Μετροσίδηρους	Μετροσίδηρους	2L		3.5	0	2025-04-07 18:07:12.298121	Created from quotation	2025-04-07 17:54:42.888905	2025-04-07 18:07:12.298986	f
241	5	Λευκόφυλλα πράσινα	Λευκόφυλλα πράσινα			4	2.5	2025-04-07 18:07:12.893875	Created from quotation	2025-04-07 17:54:43.476688	2025-04-07 18:07:12.894306	f
244	2	Θυμάρι	Θυμάρι	2L		2	0	2025-05-22 17:23:36.953378	Created from quotation	2025-04-07 17:54:45.216528	2025-05-22 17:23:36.954693	f
249	2	Λεϋλάντι	Λεϋλάντι			8	0	2025-04-07 18:07:17.820643	Created from quotation	2025-04-07 17:54:48.129155	2025-04-07 18:07:17.821026	f
250	2	Golden crest	Golden crest	5L		8	0	2025-04-07 18:07:18.423129	Created from quotation	2025-04-07 17:54:48.708534	2025-04-07 18:07:18.423758	f
258	2	Μαστίχες	Μαστίχες			0.01	0	2025-04-07 18:07:19.0399	Created from quotation	2025-04-07 18:07:19.040499	2025-04-07 18:07:19.040502	f
259	2	Πυράκανθος	Πυράκανθος			0.01	0	2025-04-07 18:07:19.63447	Created from quotation	2025-04-07 18:07:19.634961	2025-04-07 18:07:19.634963	f
253	2	Αροδάφνη 	Αροδάφνη 			3	0	2025-04-07 18:07:20.229482	Created from quotation	2025-04-07 17:54:50.464659	2025-04-07 18:07:20.229937	f
254	2	Ρομπελίνη	Ρομπελίνη			25	0	2025-04-07 18:07:20.837927	Created from quotation	2025-04-07 17:54:51.061427	2025-04-07 18:07:20.838515	f
260	2	Πυξάρι	Πυξάρι			0.01	0	2025-04-07 18:07:22.043661	Created from quotation	2025-04-07 18:07:22.044357	2025-04-07 18:07:22.044359	f
243	2	Δεντρολίβανο	Δεντρολίβανο	2L		2	0	2025-04-07 18:09:14.458928	Created from quotation	2025-04-07 17:54:44.640481	2025-04-07 18:09:14.459387	f
245	2	Λεβάντες	Λεβάντες	2L		2	0	2025-04-07 18:09:44.587419	Created from quotation	2025-04-07 17:54:45.79612	2025-04-07 18:09:44.587903	f
246	2	Φασκόμηλα	Φασκόμηλα			2	0	2025-04-07 18:09:55.959089	Created from quotation	2025-04-07 17:54:46.378659	2025-04-07 18:09:55.959508	f
261	3	Yucca rostrata	Yucca rostrata			80	50	2025-04-08 12:50:20.348089	Created from quotation	2025-04-08 12:50:20.350108	2025-04-08 12:50:20.350111	f
242	3	Τριανταφυλλιές διάφορα χρώματα	Τριανταφυλλιές διάφορα χρώματα	4L		9	5.6	2025-04-08 13:39:20.731457	Created from quotation	2025-04-07 17:54:44.064367	2025-04-08 13:39:20.732376	f
262	14	Pennisetum alopecuroides 'Little bunny'	Pennisetum alopecuroides 'Little bunny'	30cm	2L	7	4	2025-04-08 15:46:05.902742	Created from quotation	2025-04-08 15:46:05.904879	2025-04-08 15:46:05.904881	f
263	14	Tulbaghia violacea	Tulbaghia violacea	30cm	2L	3.5	0	2025-04-08 15:46:44.661617	Created from quotation	2025-04-08 15:46:44.662148	2025-04-08 15:46:44.66215	f
227	7	Fargesia robusta	Fargesia robusta	120/150cm	150cm	72	45	2025-04-08 15:48:31.238774	Created from quotation	2025-04-07 14:29:27.431807	2025-04-08 15:48:31.239293	f
233	11	Lavandula angustifolia	Lavandula angustifolia	30cm	1L/15cm	3.75	0	2025-04-08 15:55:16.816936	Created from quotation	2025-04-07 17:17:08.681928	2025-04-08 15:55:16.817363	f
125	3	ΡΥΓΧΟΣΠΕΡΜΟ	Trachelospermum jasminoides	150-170cm	170cm	40	25	2025-04-08 15:54:57.504747	\N	2025-04-05 11:31:55.273997	2025-04-08 18:14:14.295765	t
255	6	Cikkas λεπτόφυλλες	Cikkas λεπτόφυλλες			25	0	2025-04-12 11:21:47.030935	Created from quotation	2025-04-07 17:54:51.644888	2025-04-12 11:21:47.032294	f
247	5	Δάφνη	Δάφνη	2.5 lt		4	2.5	2025-04-12 13:42:37.739084	Created from quotation	2025-04-07 17:54:46.959176	2025-04-12 13:42:37.740172	f
265	14	Lavandula Pinata	Lavandula Pinata	2L		2	2	2025-04-09 11:47:59.084573	Created from quotation	2025-04-09 11:47:59.085791	2025-04-09 11:47:59.085793	f
266	2	Rosmarinus Officinalis Prostratus	Rosmarinus Officinalis Prostratus	2L		2	0	2025-04-09 11:47:59.451307	Created from quotation	2025-04-09 11:47:59.452397	2025-04-09 11:47:59.4524	f
267	2	Juniperus sp.	Juniperus sp.	2L		3	0	2025-04-09 11:47:59.819114	Created from quotation	2025-04-09 11:47:59.819914	2025-04-09 11:47:59.819916	f
268	5	'SWANE'S GOLDEN	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	5L/80cm		15	10	2025-04-09 12:05:06.098935	Created from quotation	2025-04-09 12:05:06.099844	2025-04-09 12:05:06.099846	f
270	14	Λεβαντούλα	Lavandula Pinata	2L		2	2	2025-04-09 12:05:32.974155	Created from quotation	2025-04-09 12:05:32.975048	2025-04-09 12:05:32.97505	f
273	2	Χαμαικυπάρισσο Πράσινο	Chamaecyparis lawsoniana	2L	2L	4	0	2025-04-09 14:35:24.281311	Created from quotation	2025-04-09 14:35:24.285243	2025-04-09 14:35:24.285246	f
274	5	Λαντάνα Έρπουσα	LANTANA  MONTEVIDENSIS	2L	2L	3.5	2.5	2025-04-09 14:35:24.705499	Created from quotation	2025-04-09 14:35:24.706378	2025-04-09 14:35:24.706381	f
275	5	Λαντάνα Θάμνος	Lantana Camara	2L	2L	3.5	2.5	2025-04-09 14:35:25.680402	Created from quotation	2025-04-09 14:35:25.682699	2025-04-09 14:35:25.682702	f
276	2	Μαργαρίτα Ασημόφυλλη	Gazania rigens	2L	2L	3	0	2025-04-09 14:35:26.077718	Created from quotation	2025-04-09 14:35:26.078547	2025-04-09 14:35:26.07855	f
277	11	Μελισόχορτο	Melissa officinalis	1L	1L	1.5	1	2025-04-09 14:35:26.473389	Created from quotation	2025-04-09 14:35:26.47429	2025-04-09 14:35:26.474292	f
278	15	Μελισόχορτο	Melissa officinalis	1L	1L	1.5	1	2025-04-09 14:37:43.224615	Created from quotation	2025-04-09 14:37:43.225471	2025-04-09 14:37:43.225473	f
279	3	Ficus Amstel King	Ficus binnendijkii 'Amstel King'	180cm	180cm	55	35	2025-04-09 14:51:27.263558	Created from quotation	2025-04-09 14:51:27.265089	2025-04-09 14:51:27.265091	f
281	13	Καλλιτρίδα	Καλλιτρίδα	1,5μ	1,5μ	15	0	2025-04-10 03:28:31.64512	Created from quotation	2025-04-10 03:28:31.647206	2025-04-10 03:28:31.647208	f
282	2	Αροδάφνη	Αροδάφνη	1μ	1μ	3	0	2025-04-10 03:28:32.057411	Created from quotation	2025-04-10 03:28:32.058188	2025-04-10 03:28:32.05819	f
283	5	Συκαμια Αρσενική	Συκαμια Αρσενική	1,5μ	1,5μ	45	0	2025-04-10 03:28:32.469363	Created from quotation	2025-04-10 03:28:32.470548	2025-04-10 03:28:32.47055	f
285	11	Χαρουπιά	Χαρουπιά	1,5μ	1,5μ	20	0	2025-04-10 03:28:33.291696	Created from quotation	2025-04-10 03:28:33.292651	2025-04-10 03:28:33.292654	f
286	2	ΤΟΤΕΜ	Cypress sempervirens totem	h ~ 1.4m	1.1m	15	0	2025-04-11 18:09:38.185835	Created from quotation	2025-04-11 18:09:38.188069	2025-04-11 18:09:38.188072	f
291	2	Χαμαικυπάρισσο Γκρίζο	Juniperus horizontalis gray	2.5 lt		3.5	0	2025-04-11 18:09:40.114617	Created from quotation	2025-04-11 18:09:40.115625	2025-04-11 18:09:40.115627	f
294	3	Phillyrea	Phillyrea	2.5 lt		1	0	2025-04-11 18:09:41.256438	Created from quotation	2025-04-11 18:09:41.257329	2025-04-11 18:09:41.257332	f
295	2	Μερσηνιά Ψιντρόφυλλη	Myrtus communis compacta	2.5 lt		3	0	2025-04-11 18:09:41.629642	Created from quotation	2025-04-11 18:09:41.630794	2025-04-11 18:09:41.630796	f
280	16	ΚΟΥΜ ΚΟΥΑΤ	FORTUNELLA MARGARITA	110cm		15	15	2025-04-16 03:25:55.115868	Created from quotation	2025-04-09 15:14:03.667954	2025-04-16 03:25:55.116709	f
296	11	Asparagus	Asparagus	2.5 lt		1	0	2025-04-11 18:09:42.384068	Created from quotation	2025-04-11 18:09:42.385161	2025-04-11 18:09:42.385164	f
297	2	Hyparrhenia hitra	Hyparrhenia hitra	2.5 lt		1	0	2025-04-11 18:09:42.77855	Created from quotation	2025-04-11 18:09:42.779492	2025-04-11 18:09:42.779494	f
298	3	Τριανταφυλιά Αναρρυγχώμενη Άσπρη	Rose white climbing	5lt		1	0	2025-04-11 18:09:43.150593	Created from quotation	2025-04-11 18:09:43.151478	2025-04-11 18:09:43.15148	f
300	4	Περόβσκια	Perovskia	2.5 lt		3.5	0	2025-04-11 18:09:43.904594	Created from quotation	2025-04-11 18:09:43.905585	2025-04-11 18:09:43.905587	f
287	11	Μαστιχόδεντρο	Pistacia lentiscus	5lt	10L	25	0	2025-04-12 13:16:12.558283	Created from quotation	2025-04-11 18:09:38.618666	2025-04-12 13:16:12.559914	f
290	12	Ροδιά	Punica granatun	30lt/1,8m		135	0	2025-04-12 13:17:38.3014	Created from quotation	2025-04-11 18:09:39.73913	2025-04-12 13:17:38.302808	f
289	12	Λεμονιά	Lemon tree	30 lt/1,8m		55	40	2025-04-12 13:18:38.732128	Created from quotation	2025-04-11 18:09:39.365693	2025-04-12 13:18:38.733216	f
305	12	Asparagus Meyeri	Asparagus Meyeri	2.5 lt	5L	8	6	2025-04-12 13:20:15.488588	Created from quotation	2025-04-12 13:20:15.489338	2025-04-12 13:20:15.48934	f
306	12	Phillyrea	Phillyrea	2.5 lt	10L	19.5	14.5	2025-04-12 13:22:56.517771	Created from quotation	2025-04-12 13:22:44.978052	2025-04-12 13:22:56.518343	f
303	3	Zoyssia grass	Zoyssia grass			5	3.5	2025-04-12 13:23:20.594047	Created from quotation	2025-04-11 18:09:45.068233	2025-04-12 13:23:20.594726	f
307	12	Hyparrhenia hitra	Hyparrhenia hitra	2.5 lt	2L	4.5	3	2025-04-12 13:25:43.149917	Created from quotation	2025-04-12 13:25:43.150828	2025-04-12 13:25:43.15083	f
308	2	Τριανταφυλιά Αναρρυγχώμενη Άσπρη (Παξιανή)	Rose white climbing	5lt		8	0	2025-04-12 13:26:28.768148	Created from quotation	2025-04-12 13:26:28.768913	2025-04-12 13:26:28.768915	f
292	5	Αρκοελιά	Αρκοελιά	5lt		5	0	2025-04-12 13:42:19.956271	Created from quotation	2025-04-11 18:09:40.487773	2025-04-12 13:42:19.95701	f
293	11	Δάφνη	Laurus nobilis (Bay leaf)	2.5 lt		4	0	2025-04-12 13:42:56.942244	Created from quotation	2025-04-11 18:09:40.859823	2025-04-12 13:42:56.942948	f
309	12	Περόβσκια	Perovskia	2.5 lt		3.5	2.5	2025-04-12 13:45:06.450675	Created from quotation	2025-04-12 13:45:06.451677	2025-04-12 13:45:06.451679	f
299	4	Γκαούρα Άσπρη	Gaura white	2.5 lt		3.5	2.5	2025-04-12 13:45:24.610302	Created from quotation	2025-04-11 18:09:43.527301	2025-04-12 13:45:24.611706	f
310	2	Καζουαρίνα	Καζουαρίνα	30cm		4	0	2025-04-14 15:53:47.355275	Created from quotation	2025-04-14 15:53:47.3568	2025-04-14 15:53:47.356804	f
311	2	Τερατσιές (αμαντιασμένες)	Τερατσιές (αμαντιασμένες)	80cm		8	0	2025-04-14 15:53:47.71384	Created from quotation	2025-04-14 15:53:47.714617	2025-04-14 15:53:47.714619	f
312	2	Φοινικιά Robelina	Φοινικιά Robelina	60cm h~ κορμός		70	0	2025-04-14 16:12:44.917518	Created from quotation	2025-04-14 15:53:48.068702	2025-04-14 16:12:44.91862	f
284	2	Μαστιχόδεντρο	Μαστιχόδεντρο	2lt	1,7μ	3.5	0	2025-05-14 14:04:25.992575	Created from quotation	2025-04-10 03:28:32.88952	2025-05-14 14:04:25.993078	f
271	2	Λασμαρί Foxtail	Rosmarinus Officinalis Prostratus	2L		2	0	2025-05-22 17:23:37.729721	Created from quotation	2025-04-09 12:05:54.01635	2025-05-22 17:23:37.730288	f
302	2	Ρυγχόσπερμο	Trachelospermum jasminoides	2L		3.5	0	2025-05-22 17:33:22.421673	Created from quotation	2025-04-11 18:09:44.694945	2025-05-22 17:33:22.422214	f
264	2	Cupressus sempervirens totem	Cupressus sempervirens totem	10L/1m		15	0	2025-05-07 18:22:34.640122	Created from quotation	2025-04-09 11:47:58.713914	2025-05-07 18:22:34.640678	f
272	2	ΧΑΜΑΙΚΥΠΑΡΙΣΣΟ ΓΚΡΙΖΟ	Juniperus sp.	2L		3	0	2025-05-07 18:32:42.958143	Created from quotation	2025-04-09 12:06:20.298986	2025-05-07 18:32:42.958702	f
301	2	Πιττόσπορο Νάνο	Pittosporum tobira nanum	2.5lt		3.5	0	2025-05-18 09:42:19.213133	Created from quotation	2025-04-11 18:09:44.321057	2025-05-18 09:42:19.214245	f
269	2	Totem	Cupressus sempervirens totem	10L/1m		15	0	2025-05-14 14:04:25.587842	Created from quotation	2025-04-09 12:05:19.075012	2025-05-14 14:04:25.58844	f
313	2	Κυπαρίσσι Totem Gold Gress	Κυπαρίσσι Totem Gold Gress	100 εκ		18	0	2025-04-14 15:53:48.426181	Created from quotation	2025-04-14 15:53:48.426914	2025-04-14 15:53:48.426916	f
314	2	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)	130cm		10	0	2025-04-14 15:53:48.779181	Created from quotation	2025-04-14 15:53:48.779951	2025-04-14 15:53:48.779953	f
315	2	Πασχαλιά	Πασχαλιά	40cm		10	0	2025-04-14 15:53:49.132584	Created from quotation	2025-04-14 15:53:49.133256	2025-04-14 15:53:49.133258	f
317	2	Φοινικιά Αεροκάστρουμ	Φοινικιά Αεροκάστρουμ	170cm		50	0	2025-04-14 15:53:49.863608	Created from quotation	2025-04-14 15:53:49.864363	2025-04-14 15:53:49.864365	f
320	2	Ροδιά	Ροδιά	40cm		4	0	2025-04-14 15:53:50.93709	Created from quotation	2025-04-14 15:53:50.937887	2025-04-14 15:53:50.93789	f
322	11	Μανταρινιά	Μανταρινιά	100cm		8	0	2025-04-14 15:53:51.700544	Created from quotation	2025-04-14 15:53:51.701879	2025-04-14 15:53:51.701883	f
323	11	Μεσπιλιά	Μεσπιλιά	100cm		8	0	2025-04-14 15:53:52.079594	Created from quotation	2025-04-14 15:53:52.081758	2025-04-14 15:53:52.081763	f
304	12	Μαστιχόδεντρο	Pistacia lentiscus	200 εκ	10L/2.5m	35	20	2025-04-14 16:12:44.546111	Created from quotation	2025-04-12 13:19:16.413261	2025-04-14 16:12:44.547472	f
330	3	Κυπαρίσσι Totem Gold Gress	Κυπαρίσσι Totem Gold Gress	200 εκ		55	0	2025-04-14 16:12:45.279822	Created from quotation	2025-04-14 16:12:45.280521	2025-04-14 16:12:45.280523	f
331	3	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)	Βουκεμβίλιες (2χ4 διαφορετικά χρώματα)	200 εκ		55	0	2025-04-14 16:12:45.649372	Created from quotation	2025-04-14 16:12:45.650052	2025-04-14 16:12:45.650054	f
316	2	Αρτιμαθκιά	Αρτιμαθκιά	200cm		35	0	2025-04-14 16:12:46.025755	Created from quotation	2025-04-14 15:53:49.484009	2025-04-14 16:12:46.026461	f
318	9	Ροδακινιά	Ροδακινιά	150cm		20	0	2025-04-14 16:12:46.388359	Created from quotation	2025-04-14 15:53:50.222762	2025-04-14 16:12:46.388974	f
319	9	Δαμασκηνιά	Δαμασκηνιά	150cm		20	0	2025-04-14 16:12:46.750011	Created from quotation	2025-04-14 15:53:50.578948	2025-04-14 16:12:46.750579	f
329	9	Μανταρινιά	Μανταρινιά	150cm		20	0	2025-04-14 16:12:47.121363	Created from quotation	2025-04-14 16:07:54.398518	2025-04-14 16:12:47.12196	f
328	9	Μεσπιλιά	Μεσπιλιά	150cm		20	0	2025-04-14 16:12:47.492933	Created from quotation	2025-04-14 16:07:41.02473	2025-04-14 16:12:47.493543	f
324	9	Αμυγδαλια	Αμυγδαλια	150cm		20	0	2025-04-14 16:12:47.850204	Created from quotation	2025-04-14 15:53:52.433439	2025-04-14 16:12:47.850836	f
325	9	Σαγκουίνη	Σαγκουίνη	150cm		20	0	2025-04-14 16:12:48.217313	Created from quotation	2025-04-14 15:53:52.788456	2025-04-14 16:12:48.218502	f
326	9	Πορτοκαλιά	Πορτοκαλιά	150cm		20	0	2025-04-14 16:12:48.582085	Created from quotation	2025-04-14 15:53:53.138411	2025-04-14 16:12:48.582688	f
342	9	ΒΑΛΕΝΤΣΙΑ	CITRUS SINENSIS 'VALENCIA'		ΤΑΣΠΙΝ	15	11	2025-05-08 09:27:51.426803	Created from quotation	2025-04-16 03:23:02.425535	2025-05-08 09:27:51.427357	f
333	2	Κυπαρίσσι Κιτρινο	Cupressus  sempervirens	1,5m		15	0	2025-04-15 11:24:48.354245	Created from quotation	2025-04-15 11:24:48.354942	2025-04-15 11:24:48.354944	f
334	2	Μερσυνια νανα	Myrtus communis microphylla nana	5l	5L	10	0	2025-04-15 11:24:48.75768	Created from quotation	2025-04-15 11:24:48.758315	2025-04-15 11:24:48.758318	f
335	3	Μερσηνιά Stem	Myrtus Stem	15L	15L	30	25	2025-04-15 11:24:50.011143	Created from quotation	2025-04-15 11:24:50.011798	2025-04-15 11:24:50.0118	f
332	3	Totem'	Cupressus  sempervirens	170/200cm	2M	45	35	2025-04-15 17:16:31.325155	Created from quotation	2025-04-15 11:24:47.989913	2025-04-15 17:16:31.326387	f
336	2	ΔΙΕΤΗΣ	Dietis bicolor	30cm	2L	3.5	5	2025-04-15 17:20:54.534257	Created from quotation	2025-04-15 17:20:54.536111	2025-04-15 17:20:54.536116	f
337	5	Αλτερναθήρα	Alternathera Deata	30cm	15cm	3.5	2.5	2025-04-15 17:26:03.669032	Created from quotation	2025-04-15 17:26:03.66965	2025-04-15 17:26:03.669651	f
338	3	ΓΙΑΝΝΗΣ	Bougainvillea glabra	150-170cm	2m	45	35	2025-04-15 17:31:01.720669	Created from quotation	2025-04-15 17:31:01.721322	2025-04-15 17:31:01.721324	f
339	5	ΛΑΝΤΑΝΑ ΕΡΠΩΝ	Lantana montevidensis	20cm		3.5	2.5	2025-04-15 17:31:45.278904	Created from quotation	2025-04-15 17:31:45.280823	2025-04-15 17:31:45.280827	f
343	4	ΑΛΟΗ ΒΕΡΑ	Aloe vera	30cm	5L	7	5	2025-04-16 14:26:32.380225	Created from quotation	2025-04-16 14:26:32.382124	2025-04-16 14:26:32.382127	f
345	4	Asparagus  densiflorus 'Sprengeri'	Asparagus  densiflorus 'Sprengeri'	20cm	2L	4.5	3.25	2025-04-16 14:27:10.078108	Created from quotation	2025-04-16 14:27:10.078971	2025-04-16 14:27:10.078973	f
346	10	Αεονιουμ 	aeonium	50cm	7L	15	8	2025-04-17 13:06:31.188658	Created from quotation	2025-04-16 14:29:16.563205	2025-04-17 13:06:31.191115	f
347	2	Χαμέροπς	Chamaerops humilis			40	0	2025-04-17 13:08:22.684949	Created from quotation	2025-04-17 13:08:22.686268	2025-04-17 13:08:22.68627	f
348	14	EUGENIA ETNA FIRE	EUGENIA ETNA FIRE	4L		8	6	2025-04-17 13:33:36.953011	Created from quotation	2025-04-17 13:33:36.953829	2025-04-17 13:33:36.953831	f
349	14	MAGNOLIA GRANDIFLORA	MAGNOLIA GRANDIFLORA	1,5m		52	40	2025-04-17 13:34:05.875766	Created from quotation	2025-04-17 13:34:05.876458	2025-04-17 13:34:05.876461	f
351	11	TRADESCANTIA PALLIDA 'PURPLE HEART'	TRADESCANTIA PALLIDA 'PURPLE HEART'	None	1L	2.5	2	2025-04-17 13:35:58.679164	Created from quotation	2025-04-17 13:35:58.680166	2025-04-17 13:35:58.680171	f
353	17	ΛΕΜΟΝΙΑ	CITRUS LIMON			55	40	2025-04-17 13:46:53.308507	Created from quotation	2025-04-17 13:46:53.311667	2025-04-17 13:46:53.311671	f
354	17	ΚΛΕΜΕΝΤΙΝΗ	CITRUS MANDARINE			55	40	2025-04-17 13:47:06.347752	Created from quotation	2025-04-17 13:47:06.348474	2025-04-17 13:47:06.348477	f
355	3	MAGNOLIA GRANDIFLORA	MAGNOLIA GRANDIFLORA	1,5m		52	65	2025-04-17 14:05:20.454939	Created from quotation	2025-04-17 14:05:20.455607	2025-04-17 14:05:20.455608	f
356	3	Αλοκάσια	Alocasia			40	0	2025-04-18 03:46:10.216745	Created from quotation	2025-04-18 03:46:10.218271	2025-04-18 03:46:10.218274	f
357	2	ΣΥΚΙΑ ΛΑΪΚΙΑΝΗ	ΣΥΚΙΑ ΛΑΪΚΙΑΝΗ			3.5	0	2025-04-27 07:29:45.05287	Created from quotation	2025-04-27 07:29:45.054408	2025-04-27 07:29:45.054412	f
358	11	Συκαμιά 				8	0	2025-04-27 07:29:45.413537	Created from quotation	2025-04-27 07:29:45.41416	2025-04-27 07:29:45.414162	f
359	3	ΜΑΓΝΟΛΙΕΣ	ΜΑΓΝΟΛΙΕΣ			80	0	2025-04-27 07:29:45.769512	Created from quotation	2025-04-27 07:29:45.770176	2025-04-27 07:29:45.770178	f
360	2	ΚΙΤΡΟΜΗΛΙΑ	ΚΙΤΡΟΜΗΛΙΑ			6	0	2025-04-27 07:29:46.123804	Created from quotation	2025-04-27 07:29:46.124409	2025-04-27 07:29:46.124411	f
327	9	Λεμονιά	Λεμονιά	2m		35	25	2025-04-30 12:29:50.635689	Created from quotation	2025-04-14 15:53:53.487184	2025-04-30 12:29:50.636574	f
350	11	STRELITZIA NICOLAI	STRELITZIA NICOLAI	5L/1,3m		15	10	2025-05-25 11:16:52.74407	Created from quotation	2025-04-17 13:35:34.887006	2025-05-25 11:16:52.744811	f
341	9	ΛΕΜΟΝΙΑ	CITRUS LIMON	8-10 Girth	ΤΑΣΠΙΝ	40	25	2025-05-15 13:02:36.085319	Created from quotation	2025-04-16 03:22:40.08864	2025-05-15 13:02:36.086155	f
340	9	ΚΛΕΜΕΝΤΙΝΗ	CITRUS MANDARINE		ΤΑΣΠΙΝ	15	11	2025-05-08 09:27:35.212243	Created from quotation	2025-04-16 03:22:16.793594	2025-05-08 09:27:35.212774	f
344	6	Philodendron xanadu	Philodendron xanadu	5-7lit	2L	5	3.5	2025-05-25 11:21:35.402956	Created from quotation	2025-04-16 14:26:56.061024	2025-05-25 11:21:35.403948	f
361	9	ΚΕΡΑΣΙΕΣ ΓΙΑ ΗΜΙΟΡΕΙΝΑ	ΚΕΡΑΣΙΕΣ ΓΙΑ ΗΜΙΟΡΕΙΝΑ			8	0	2025-04-27 07:29:46.476475	Created from quotation	2025-04-27 07:29:46.477107	2025-04-27 07:29:46.477108	f
362	2	ΦΟΙΝΙΚΙΕΣ ΑΠΕΚΑΣΤΡΩΜΕΝΕΣ (ΛΙΓΟ ΜΕΓΑΛΕΣ)	ΦΟΙΝΙΚΙΕΣ ΑΠΕΚΑΣΤΡΩΜΕΝΕΣ (ΛΙΓΟ ΜΕΓΑΛΕΣ)			35	0	2025-04-27 07:29:46.828456	Created from quotation	2025-04-27 07:29:46.829297	2025-04-27 07:29:46.8293	f
363	2	ΠΑΚΙΣΤΑΝΟΥΣ	ΠΑΚΙΣΤΑΝΟΥΣ			0	0	2025-04-27 07:29:47.180502	Created from quotation	2025-04-27 07:29:47.18118	2025-04-27 07:29:47.181182	f
364	2	ΑΓΙΟΚΛΗΜΑ	ΑΓΙΟΚΛΗΜΑ			4	0	2025-04-27 07:29:47.532528	Created from quotation	2025-04-27 07:29:47.53318	2025-04-27 07:29:47.533181	f
365	11	ΦΟΥΛΙ	ΦΟΥΛΙ			0	0	2025-04-27 07:29:47.89218	Created from quotation	2025-04-27 07:29:47.892816	2025-04-27 07:29:47.892818	f
366	5	ΓΑΡΔΕΝΙΑ ΔΕΝΤΡΟ (ΟΧΙ ΦΥΤΟ)	ΓΑΡΔΕΝΙΑ ΔΕΝΤΡΟ (ΟΧΙ ΦΥΤΟ)			25	0	2025-04-27 07:29:48.260516	Created from quotation	2025-04-27 07:29:48.261153	2025-04-27 07:29:48.261156	f
367	2	ΓΙΑΣΕΜΙ ΜΠΛΕ	ΓΙΑΣΕΜΙ ΜΠΛΕ			4	0	2025-04-27 07:29:48.617062	Created from quotation	2025-04-27 07:29:48.61769	2025-04-27 07:29:48.617693	f
368	3	ΟΡΤΑΝΣΙΕΣ	ΟΡΤΑΝΣΙΕΣ			15	0	2025-04-27 07:29:48.976021	Created from quotation	2025-04-27 07:29:48.976645	2025-04-27 07:29:48.976647	f
369	11	ΚΑΜΕΛΙΑ	ΚΑΜΕΛΙΑ			0	0	2025-04-27 07:29:49.332485	Created from quotation	2025-04-27 07:29:49.333133	2025-04-27 07:29:49.333135	f
370	11	ΓΟΥΙΣΤΕΡΙΕΣ	ΓΟΥΙΣΤΕΡΙΕΣ			30	0	2025-04-27 07:29:49.695745	Created from quotation	2025-04-27 07:29:49.696506	2025-04-27 07:29:49.696509	f
371	11	Συκαμιά Μαύρη				8	0	2025-04-27 07:31:12.336601	Created from quotation	2025-04-27 07:31:12.33735	2025-04-27 07:31:12.337353	f
372	11	Συκαμιά Άσπρη				8	0	2025-04-27 07:31:49.485499	Created from quotation	2025-04-27 07:31:49.486101	2025-04-27 07:31:49.486103	f
373	11	Τζιακαράντα	Jacaranda 	2m		1	0	2025-04-29 17:52:58.22017	Created from quotation	2025-04-29 17:52:58.221786	2025-04-29 17:52:58.221789	f
374	11	Πεύκος Ήμερος	Pinus pinea	1,7m		1	0	2025-04-29 17:52:58.626033	Created from quotation	2025-04-29 17:52:58.62673	2025-04-29 17:52:58.626732	f
321	2	Συκιά	Συκιά	2lt		3.5	0	2025-04-29 17:52:59.005013	Created from quotation	2025-04-14 15:53:51.291963	2025-04-29 17:52:59.006206	f
377	16	Συκαμιά Κόκκινο Κοντό			Σακκούλη	8	0	2025-04-29 17:56:04.872364	Created from quotation	2025-04-29 17:56:04.873157	2025-04-29 17:56:04.873159	f
378	11	Συκαμιά Κόκκινο Μακρή				8	0	2025-04-29 17:56:27.675897	Created from quotation	2025-04-29 17:56:27.6766	2025-04-29 17:56:27.676601	f
379	11	Συκαμιά Άσπρη Κοντό				8	0	2025-04-29 17:56:58.018727	Created from quotation	2025-04-29 17:56:58.019396	2025-04-29 17:56:58.019398	f
380	9	Συκαμιά Άσπρη Μακρή				8	0	2025-04-29 18:11:09.421	Created from quotation	2025-04-29 18:11:09.421669	2025-04-29 18:11:09.421671	f
381	9	Συκαμιά Κόκκινο Κοντό			Σακκούλη	8	0	2025-04-29 18:11:20.102402	Created from quotation	2025-04-29 18:11:20.103032	2025-04-29 18:11:20.103034	f
382	9	Συκαμιά Άσπρη Κοντό				8	0	2025-04-29 18:11:33.473878	Created from quotation	2025-04-29 18:11:33.474535	2025-04-29 18:11:33.474537	f
383	9	Συκαμιά Κόκκινο Μακρή				8	0	2025-04-29 18:11:54.126337	Created from quotation	2025-04-29 18:11:54.126933	2025-04-29 18:11:54.126935	f
384	4	Τζιακαράντα	Jacaranda 	2m		35	25	2025-04-30 08:30:55.28753	Created from quotation	2025-04-30 08:30:55.289381	2025-04-30 08:30:55.289384	f
385	4	Πεύκος Ήμερος	Pinus pinea	1,7m		26	20	2025-04-30 08:31:43.93423	Created from quotation	2025-04-30 08:31:35.310759	2025-04-30 08:31:43.935246	f
386	3	Ευγενία Etna Fire 	Eugenia Etna Fire 	180 cm	160cm	22	20	2025-04-30 12:29:47.598132	Created from quotation	2025-04-30 12:29:47.59946	2025-04-30 12:29:47.599461	f
387	2	Πιττόσπορα Νάνα	Pittosporum Nana 	2L		3	0	2025-04-30 12:29:47.969753	Created from quotation	2025-04-30 12:29:47.970372	2025-04-30 12:29:47.970374	f
389	11	Date Palm 	Date Palm 	2m	150cm	35	25	2025-04-30 12:29:48.740186	Created from quotation	2025-04-30 12:29:48.740852	2025-04-30 12:29:48.740854	f
390	2	Χαμαίρωπας	Chamaerops Humilis	70cm	70cm	45	0	2025-04-30 12:29:49.147708	Created from quotation	2025-04-30 12:29:49.148242	2025-04-30 12:29:49.148244	f
375	2	Αγάπανθος	Agapanthus	2L		3.5	0	2025-04-30 12:29:49.515061	Created from quotation	2025-04-29 17:52:59.379106	2025-04-30 12:29:49.515923	f
391	6	Σέλουμ	Sellum			4.5	3.5	2025-04-30 12:29:49.87058	Created from quotation	2025-04-30 12:29:49.871297	2025-04-30 12:29:49.871299	f
392	12	Washingtonian Palm 	Washingtonian Palm 	2m		200	160	2025-04-30 12:29:50.227909	Created from quotation	2025-04-30 12:29:50.228489	2025-04-30 12:29:50.228491	f
393	12	Γιασεμί Γαλλικό	Jasmin (2 m)	2m	2m	22	16	2025-04-30 12:29:51.106518	Created from quotation	2025-04-30 12:29:51.107144	2025-04-30 12:29:51.107146	f
394	14	Αρέκα	Areca Palm (2 m)	2m		150	100	2025-04-30 12:29:51.473417	Created from quotation	2025-04-30 12:29:51.474046	2025-04-30 12:29:51.474048	f
388	12	Λιγούστρο	Ligustrum 	150cm		20	14	2025-04-30 12:31:05.340878	Created from quotation	2025-04-30 12:29:48.334273	2025-04-30 12:31:05.341706	f
395	18	Date Palm 	Date Palm 	2m	150cm	35	25	2025-04-30 12:31:27.139367	Created from quotation	2025-04-30 12:31:27.139962	2025-04-30 12:31:27.139964	f
396	18	Λεμονιά	Lemon Tree 	2m	180cm	35	25	2025-04-30 12:32:52.175766	Created from quotation	2025-04-30 12:32:52.176366	2025-04-30 12:32:52.176367	f
397	18	Γιασεμί Γαλλικό	Jasmin 	2m	2m	22	16	2025-04-30 12:33:07.607809	Created from quotation	2025-04-30 12:33:07.6084	2025-04-30 12:33:07.608402	f
398	18	Αρέκα	Areca Palm	2m		150	100	2025-04-30 12:33:20.162097	Created from quotation	2025-04-30 12:33:20.162676	2025-04-30 12:33:20.162678	f
399	5	ΡΟΔΙΑ	PUNICA GRANATUM		ΤΑΣΠΙΝ	15	10	2025-05-01 19:34:24.57545	Created from quotation	2025-05-01 19:34:24.57735	2025-05-01 19:34:24.577353	f
400	2	ΣΤΡΕΛΙΤΣΙΑ ΝΙΚΟΛΑΕ	STRELITZIA NICOLAI			15	10	2025-05-01 19:37:06.614955	Created from quotation	2025-05-01 19:37:06.616011	2025-05-01 19:37:06.616014	f
401	5	Tipuana Tipu Tree	Tipuana Tipu Tree	1,5 m	1m/2L	4.5	3	2025-05-03 13:29:23.835824	Created from quotation	2025-05-03 13:29:23.949921	2025-05-03 13:29:23.949926	f
402	7	Συκαμιά καλλωπιστική πλατύφυλλη άκαρπη	Συκαμιά καλλωπιστική πλατύφυλλη άκαρπη	1,5 m	1.5m/7L	18	12	2025-05-03 13:29:24.34661	Created from quotation	2025-05-03 13:29:24.347215	2025-05-03 13:29:24.347217	f
403	2	Καλλιστήμονας	Καλλιστήμονας	1,5 m	1.5m/10L	15	0	2025-05-03 13:29:24.739856	Created from quotation	2025-05-03 13:29:24.740529	2025-05-03 13:29:24.740531	f
404	4	Βραχυχύτων	Kurrajong Tree	1,5 m	1.5μ	12	8	2025-05-03 13:29:25.133196	Created from quotation	2025-05-03 13:29:25.133853	2025-05-03 13:29:25.133855	f
405	2	Λασμαρί	Λασμαρί	20 cm	20cm/2L	2	0	2025-05-03 13:29:25.527711	Created from quotation	2025-05-03 13:29:25.528303	2025-05-03 13:29:25.528304	f
406	2	Χαμομήλι	Χαμομήλι	20 cm		1	0	2025-05-03 13:29:25.876971	Created from quotation	2025-05-03 13:29:25.877549	2025-05-03 13:29:25.877551	f
407	2	Αχίλλεια	Αχίλλεια	20 cm		1	0	2025-05-03 13:29:26.226029	Created from quotation	2025-05-03 13:29:26.226641	2025-05-03 13:29:26.226643	f
408	2	Μετροσίδερος	Metrosideros	50 cm/5L	25cm/5L	7	0	2025-05-03 13:29:26.62004	Created from quotation	2025-05-03 13:29:26.620736	2025-05-03 13:29:26.620738	f
409	2	Τούραντα Άσπρη	Duranta White	50 cm		1	0	2025-05-03 13:29:26.973511	Created from quotation	2025-05-03 13:29:26.974153	2025-05-03 13:29:26.974155	f
410	2	Λευκόφυλλο Πράσινο	Leucophyllum	50 cm	13cm/2L	3	0	2025-05-03 13:29:27.38866	Created from quotation	2025-05-03 13:29:27.389213	2025-05-03 13:29:27.389215	f
411	2	Μερσηνια	Μερσηνια	50 cm	25cm/5L	8	0	2025-05-03 13:29:27.832327	Created from quotation	2025-05-03 13:29:27.833006	2025-05-03 13:29:27.833009	f
413	9	Συκαμιά καλλωπιστική πλατύφυλλη άκαρπη	Συκαμιά καλλωπιστική πλατύφυλλη άκαρπη	1,5 m	1.5m/7L	18	12	2025-05-03 13:30:29.912315	Created from quotation	2025-05-03 13:30:29.912968	2025-05-03 13:30:29.91297	f
352	14	TRADESCANTIA PALLIDA 'PURPLE HEART'	TRADESCANTIA PALLIDA 'PURPLE HEART'	None	1L	2.5	2	2025-05-07 14:20:38.215725	Created from quotation	2025-04-17 13:36:51.8853	2025-05-07 14:20:38.216229	f
432	13	Αριζόνικο	CUPRESSUS ARIZONICA		1m	13	10	2025-05-08 09:18:21.35741	Created from quotation	2025-05-07 18:29:45.403277	2025-05-08 09:18:21.358271	f
425	2	PUNICA GRANATUM	PUNICA GRANATUM			10	0	2025-05-07 18:22:31.488704	Created from quotation	2025-05-07 18:22:31.490349	2025-05-07 18:22:31.490353	f
438	2	ΑΡΧΟΝΤΟΦΟΙΝΙΚΑΣ	ΑΡΧΟΝΤΟΦΟΙΝΙΚΑΣ	5L (SIZE B)	5L (SIZE B)	20	0	2025-05-09 18:11:43.499972	Created from quotation	2025-05-09 18:11:43.501729	2025-05-09 18:11:43.501732	f
415	2	CITRUS LIMON	CITRUS LIMON			15	0	2025-05-07 18:22:32.89438	Created from quotation	2025-05-07 14:20:33.733788	2025-05-07 18:22:32.895395	f
416	2	CITRUS MANDARINE	CITRUS MANDARINE			15	0	2025-05-07 18:22:33.240721	Created from quotation	2025-05-07 14:20:34.081344	2025-05-07 18:22:33.241252	f
426	2	CITRUS SINENSIS 'VALENCIA'	CITRUS SINENSIS 'VALENCIA'			15	0	2025-05-07 18:22:33.597338	Created from quotation	2025-05-07 18:22:33.598002	2025-05-07 18:22:33.598004	f
427	2	CUPRESSUS ARIZONICA	CUPRESSUS ARIZONICA			12	0	2025-05-07 18:22:33.94531	Created from quotation	2025-05-07 18:22:33.945937	2025-05-07 18:22:33.945939	f
417	2	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'	CUPRESSUS SEMPERVIRENS 'SWANE'S GOLDEN'		80cm	15	0	2025-05-07 18:22:34.293536	Created from quotation	2025-05-07 14:20:34.482842	2025-05-07 18:22:34.294022	f
421	2	LIMONIUM SINUATUM	LIMONIUM 		2L	2.75	0	2025-05-07 18:22:36.730682	Created from quotation	2025-05-07 14:20:36.831438	2025-05-07 18:22:36.731278	f
428	2	METROSIDEROS EXCELSA	METROSIDEROS EXCELSA			3	0	2025-05-07 18:22:37.083313	Created from quotation	2025-05-07 18:22:37.083988	2025-05-07 18:22:37.08399	f
429	2	MYRTUS COMMUNIS 'COMPACTA'	MYRTUS COMMUNIS 'COMPACTA'			2.75	0	2025-05-07 18:22:37.429048	Created from quotation	2025-05-07 18:22:37.429678	2025-05-07 18:22:37.42968	f
430	2	OLEA EUROPAEA STEM	OLEA EUROPAEA STEM			0.01	0	2025-05-07 18:22:37.780355	Created from quotation	2025-05-07 18:22:37.78109	2025-05-07 18:22:37.781092	f
423	4	PRUNUS CERASIFERA 'KRAUTER VESUVIUS'	PRUNUS CERASIFERA 'KRAUTER VESUVIUS'			45	35	2025-05-07 18:22:38.847541	Created from quotation	2025-05-07 14:20:37.524154	2025-05-07 18:22:38.848065	f
414	2	ALTERNANTHERA	ALTERNANTHERA		2L	3	0	2025-05-07 18:27:15.279859	Created from quotation	2025-05-07 14:20:32.980805	2025-05-07 18:27:15.280505	f
457	2	ΒΙΒΟΥΡΝΟ ΛΟΥΣΙΤΟΥΜ	Viburnum tinus 'Lucidum'	80-120cm	5L/50cm	8	0	2025-05-10 17:58:23.713499	Created from quotation	2025-05-10 17:58:23.714263	2025-05-10 17:58:23.714265	f
419	2	ELAEAGNUS X EBBINGEI	ELAEAGNUS X EBBINGEI		2L	3	0	2025-05-07 18:32:23.471374	Created from quotation	2025-05-07 14:20:36.048189	2025-05-07 18:32:23.472293	f
420	2	LAVANDULA PINNATA	LAVANDULA PINNATA		2L	2	0	2025-05-07 18:33:03.580443	Created from quotation	2025-05-07 14:20:36.439731	2025-05-07 18:33:03.58119	f
434	2	Λιμονιουμ	LIMONIUM		2L	2.75	0	2025-05-07 18:33:33.921613	Created from quotation	2025-05-07 18:33:33.92227	2025-05-07 18:33:33.922272	f
435	2	Μετροσίδερο	METROSIDEROS EXCELSA		2L	3	0	2025-05-07 18:33:59.157431	Created from quotation	2025-05-07 18:33:59.158067	2025-05-07 18:33:59.158069	f
431	2	ΡΟΔΙΑ	PUNICA GRANATUM		10L	20	0	2025-05-15 13:10:14.470178	Created from quotation	2025-05-07 18:26:05.072495	2025-05-15 13:10:14.470668	f
424	4	STIPA TENUISSIMA	STIPA TENUISSIMA			2.5	0	2025-05-08 09:12:01.381611	Created from quotation	2025-05-07 14:20:37.869834	2025-05-08 09:12:01.382839	f
436	2	Μερσινιά μίνι	MYRTUS COMMUNIS 'COMPACTA'		2L	3	0	2025-05-08 09:17:28.117173	Created from quotation	2025-05-07 18:34:22.744634	2025-05-08 09:17:28.117705	f
454	2	ΤΡΙΑΝΤΑΦΥΛΛΙΑ	ΤΡΙΑΝΤΑΦΥΛΛΙΑ		2L	8	0	2025-05-09 18:11:50.519922	Created from quotation	2025-05-09 18:11:50.52064	2025-05-09 18:11:50.520642	f
449	2	BASIL	BASIL		2L	1.5	0	2025-05-12 13:49:27.186624	Created from quotation	2025-05-09 18:11:48.434554	2025-05-12 13:49:27.187559	f
455	2	ΣΤΡΕΛΙΤΣΙΑ NICOLAI	STRELITZIA NICOLAI	5L	5L	10	0	2025-05-09 18:13:04.576719	Created from quotation	2025-05-09 18:13:04.577527	2025-05-09 18:13:04.57753	f
440	2	ELEAGNOUS GREEN	ELEAGNOUS GREEN	2L	2L	3.5	0	2025-05-09 18:13:22.250104	Created from quotation	2025-05-09 18:11:44.77762	2025-05-09 18:13:22.250633	f
441	2	CARISSA	CARISSA	2L	2L	3	0	2025-05-09 18:13:36.133134	Created from quotation	2025-05-09 18:11:45.183989	2025-05-09 18:13:36.133697	f
442	2	ELEAGNOUS YELLOW	ELEAGNOUS YELLOW	2L	2L	3.5	0	2025-05-09 18:13:59.05208	Created from quotation	2025-05-09 18:11:45.58539	2025-05-09 18:13:59.052591	f
439	2	VIVORNO LUCIDUM	VIVORNO LUCIDUM	2L	2L	3.5	0	2025-05-12 13:49:02.948643	Created from quotation	2025-05-09 18:11:43.938479	2025-05-12 13:49:02.949182	f
444	2	ZANTOKSILO	ZANTOKSILO	2L	2L	4	0	2025-05-09 18:14:26.5875	Created from quotation	2025-05-09 18:11:46.402284	2025-05-09 18:14:26.588102	f
446	2	ORIGANO	ORIGANO		2L	2	0	2025-05-09 18:15:19.118208	Created from quotation	2025-05-09 18:11:47.209662	2025-05-09 18:15:19.118866	f
447	2	LEVANDA PINATA	LEVANDA PINATA		2L	2	0	2025-05-09 18:15:38.204957	Created from quotation	2025-05-09 18:11:47.614267	2025-05-09 18:15:38.205475	f
445	2	ROSEMARY	ROSEMARY		2L	2	0	2025-05-09 18:15:10.251297	Created from quotation	2025-05-09 18:11:46.806498	2025-05-09 18:15:10.251868	f
448	2	LEVANDA GRAY	LEVANDA GRAY		2L	2	0	2025-05-09 18:15:55.792639	Created from quotation	2025-05-09 18:11:48.023739	2025-05-09 18:15:55.793213	f
450	2	ΘΥΜΑΡΙ	ΘΥΜΑΡΙ		2L	2	0	2025-05-09 18:16:16.936747	Created from quotation	2025-05-09 18:11:48.835733	2025-05-09 18:16:16.938154	f
451	2	AGAPANTHUS	AGAPANTHUS	2L	2L	4	0	2025-05-09 18:16:32.851976	Created from quotation	2025-05-09 18:11:49.245912	2025-05-09 18:16:32.852554	f
452	2	FESTUGA	FESTUGA	2L	2L	4	0	2025-05-09 18:16:46.375665	Created from quotation	2025-05-09 18:11:49.677923	2025-05-09 18:16:46.376267	f
453	2	TULBAGHIA	TULBAGHIA	2L	2L	2.5	0	2025-05-09 18:17:07.11732	Created from quotation	2025-05-09 18:11:50.083105	2025-05-09 18:17:07.117927	f
456	5	Κονβολβουλος	Convolvulus cneorum		2L	4	2.5	2025-05-10 17:51:53.526626	Created from quotation	2025-05-10 17:51:53.528432	2025-05-10 17:51:53.528436	f
459	9	Citrus reticulata	Citrus reticulata	8-10 Girth	200cm	1	0	2025-05-14 13:18:52.791939	Created from quotation	2025-05-12 17:24:26.108607	2025-05-14 13:18:52.792886	f
443	2	DURANDA GOLD	DURANDA GOLD	2L	2L	3.5	0	2025-05-12 13:47:44.075324	Created from quotation	2025-05-09 18:11:45.9945	2025-05-12 13:47:44.076538	f
422	2	OLEA EUROPAEA	OLEA EUROPAEA	50lit		250	0	2025-05-25 10:48:56.899276	Created from quotation	2025-05-07 14:20:37.176495	2025-05-25 10:48:56.89968	f
412	2	Λεβάντα	Λεβάντα	20 cm	15cm/2L	2	0	2025-05-14 14:04:23.611458	Created from quotation	2025-05-03 13:29:28.227016	2025-05-14 14:04:23.611933	f
433	2	Ελαίαγνος Πράσινος	ELAEAGNUS X EBBINGEI	5lit		7	0	2025-05-15 13:18:20.546071	Created from quotation	2025-05-07 18:32:14.090985	2025-05-15 13:18:20.546561	f
462	7	Lagerstroemia indica	Lagerstroemia indica	8-10 Girth	150cm	15	0	2025-05-12 17:24:28.213428	Created from quotation	2025-05-12 17:24:28.214155	2025-05-12 17:24:28.214159	f
472	2	Pennisetum alopecuroides 'Little bunny'	Pennisetum alopecuroides 'Little bunny'	2-3lit	50cm	1	0	2025-05-12 17:24:36.010801	Created from quotation	2025-05-12 17:24:36.011555	2025-05-12 17:24:36.011558	f
473	2	Duranta alba	Duranta alba	5lit	80cm	1	0	2025-05-12 17:24:36.977302	Created from quotation	2025-05-12 17:24:36.978857	2025-05-12 17:24:36.978861	f
474	5	Convolvulus sabatius	Convolvulus sabatius	2/3lit	20cm	3.5	0	2025-05-12 17:24:37.995404	Created from quotation	2025-05-12 17:24:37.996319	2025-05-12 17:24:37.996323	f
477	3	Pistacia lentiscus	Pistacia lentiscus	5lit	80cm	1	0	2025-05-12 17:24:40.309273	Created from quotation	2025-05-12 17:24:40.309996	2025-05-12 17:24:40.309999	f
460	9	Citrus sinensis	Citrus sinensis	8-10 Girth	200cm	1	0	2025-05-14 13:19:37.439335	Created from quotation	2025-05-12 17:24:26.867352	2025-05-14 13:19:37.439916	f
467	9	Punica granatum	Punica granatum		150cm	20	0	2025-05-14 13:26:16.475192	Created from quotation	2025-05-12 17:24:31.528637	2025-05-14 13:26:16.475738	f
470	2	Agapanthus africanus	Agapanthus africanus	2-3lit	30cm	7	0	2025-05-14 13:34:13.466554	Created from quotation	2025-05-12 17:24:33.50298	2025-05-14 13:34:13.467112	f
471	2	Dietes grandiflora	Dietes grandiflora	2-3lit	30cm	3.5	0	2025-05-14 13:38:28.791714	Created from quotation	2025-05-12 17:24:34.683158	2025-05-14 13:38:28.792251	f
475	2	Gaura lindtheimeri	Gaura lindtheimeri	2/3lit	30cm	3	0	2025-05-14 13:42:03.155102	Created from quotation	2025-05-12 17:24:38.878743	2025-05-14 13:42:03.155749	f
476	11	Laurus nobilis	Laurus nobilis	5lit	80cm	3.5	0	2025-05-14 13:42:21.262493	Created from quotation	2025-05-12 17:24:39.340799	2025-05-14 13:42:21.263424	f
506	2	PEATOMOSS	PEATOMOSS	70L		9.65	0	2025-05-15 13:29:36.418267	Created from quotation	2025-05-15 12:47:35.571114	2025-05-15 13:29:36.418773	f
487	3	Μακνόλια	Μακνόλια			80	52	2025-05-14 14:04:24.837548	Created from quotation	2025-05-14 14:04:24.838162	2025-05-14 14:04:24.838164	f
488	2	Ficus Amstel King	Ficus Amstel King			5	0	2025-05-14 14:04:25.214894	Created from quotation	2025-05-14 14:04:25.215485	2025-05-14 14:04:25.215486	f
489	2	Ευκάλυπτος Στρογγυλόφιλλος	Ευκάλυπτος Στρογγυλόφιλλος			7	0	2025-05-14 14:04:26.354191	Created from quotation	2025-05-14 14:04:26.354821	2025-05-14 14:04:26.354823	f
490	2	Πιττόσπορο Νάνα	Πιττόσπορο Νάνα			3	0	2025-05-14 14:04:26.741704	Created from quotation	2025-05-14 14:04:26.742329	2025-05-14 14:04:26.74233	f
491	2	Λασμαρί Έρπων	Λασμαρί Έρπων			2	0	2025-05-14 14:04:27.538658	Created from quotation	2025-05-14 14:04:27.539311	2025-05-14 14:04:27.539313	f
493	2	Κοκκινόφυλλη	Κοκκινόφυλλη			0	0	2025-05-14 14:04:28.34974	Created from quotation	2025-05-14 14:04:28.350381	2025-05-14 14:04:28.350382	f
495	11	Ευγενία Έτνα 	Ευγενία Έτνα 			0	0	2025-05-14 14:04:29.080156	Created from quotation	2025-05-14 14:04:29.080795	2025-05-14 14:04:29.080796	f
496	11	Συζύγιο	Συζύγιο			0	0	2025-05-14 14:04:29.443358	Created from quotation	2025-05-14 14:04:29.444014	2025-05-14 14:04:29.444016	f
497	3	Ευγενία Έτνα 	Ευγενία Έτνα 		170cm	28	16	2025-05-15 12:19:54.432413	Created from quotation	2025-05-15 12:19:54.434353	2025-05-15 12:19:54.434355	f
498	5	Κοκκινόφυλλη	Κοκκινόφυλλη			18	12	2025-05-15 12:20:26.215952	Created from quotation	2025-05-15 12:20:26.216636	2025-05-15 12:20:26.216637	f
499	6	Λεμονιά Eureka	Λεμονιά Eureka	7Λ		18	0	2025-05-15 12:47:32.953843	Created from quotation	2025-05-15 12:47:32.955365	2025-05-15 12:47:32.955367	f
500	6	ΓΙΑΦΗΤΙΚΗ	ΓΙΑΦΗΤΙΚΗ	7Λ		18	0	2025-05-15 12:47:33.329522	Created from quotation	2025-05-15 12:47:33.330182	2025-05-15 12:47:33.330185	f
501	6	ΜΕΡΛΙΝ	ΜΕΡΛΙΝ	7Λ		18	0	2025-05-15 12:47:33.689898	Created from quotation	2025-05-15 12:47:33.690691	2025-05-15 12:47:33.690692	f
502	6	ΚΛΕΜΕΝΤΙΝΗ	ΚΛΕΜΕΝΤΙΝΗ	7Λ		18	0	2025-05-15 12:47:34.062695	Created from quotation	2025-05-15 12:47:34.063343	2025-05-15 12:47:34.063345	f
503	6	ΑΡΑΚΑΠΑ	ΑΡΑΚΑΠΑ	7Λ		18	0	2025-05-15 12:47:34.46356	Created from quotation	2025-05-15 12:47:34.464224	2025-05-15 12:47:34.464225	f
504	5	ΛΑΝΤΑΝΑ ΠΟΡΤΟΚΑΛΙΑ	ΛΑΝΤΑΝΑ ΠΟΡΤΟΚΑΛΙΑ	7Λ		4	0	2025-05-15 12:47:34.834937	Created from quotation	2025-05-15 12:47:34.835534	2025-05-15 12:47:34.835536	f
505	2	ΠΕΡΛΙΤΗΣ	ΠΕΡΛΙΤΗΣ			18	0	2025-05-15 12:47:35.205857	Created from quotation	2025-05-15 12:47:35.206766	2025-05-15 12:47:35.206768	f
482	4	Διανέλλα	Dianella tasmanica	2-3lit	30cm	8	6	2025-05-15 13:12:51.024916	Created from quotation	2025-05-14 13:38:17.33291	2025-05-15 13:12:51.02542	f
479	3	Trachelospermum jasminoides	Trachelospermum jasminoides	5lit	150-170cm	16	12	2025-05-15 13:16:41.904554	Created from quotation	2025-05-12 17:24:41.400685	2025-05-15 13:16:41.905054	f
480	4	Perovskia artipilicifolia	Perovskia artipilicifolia	2-3lit	30cm	4	3	2025-05-15 13:17:14.499661	Created from quotation	2025-05-12 17:24:41.936488	2025-05-15 13:17:14.500155	f
478	2	Pittosporum tobira 'Nana'	Pittosporum tobira 'Nana'	2/3lit	30cm	3	0	2025-05-25 11:21:47.1697	Created from quotation	2025-05-12 17:24:40.903141	2025-05-25 11:21:47.170288	f
492	2	Αλτερναθυρα	Αλτερναθυρα			3	0	2025-05-21 12:59:14.06361	Created from quotation	2025-05-14 14:04:27.94602	2025-05-21 12:59:14.065014	f
418	2	ELAEAGNUS PUNGENS	ELAEAGNUS PUNGENS	5lit	2L	7	0	2025-05-25 10:49:04.375609	Created from quotation	2025-05-07 14:20:35.655105	2025-05-25 10:49:04.376155	f
494	2	Ελαίαγνος Δίχρωμος	Ελαίαγνος Δίχρωμος			3.5	0	2025-05-21 12:59:46.730553	Created from quotation	2025-05-14 14:04:28.715029	2025-05-21 12:59:46.731226	f
484	2	Λασμαρί Ορθόκλαδο	Λασμαρί Ορθόκλαδο		2L	2	0	2025-05-21 13:00:13.088007	Created from quotation	2025-05-14 14:04:23.198336	2025-05-21 13:00:13.088874	f
485	2	Μερσηνιά	Μερσηνιά		2L	3	0	2025-05-21 13:00:29.634687	Created from quotation	2025-05-14 14:04:24.04588	2025-05-21 13:00:29.635416	f
486	2	Ζαντόξυλο	Ζαντόξυλο		2L	4	0	2025-05-21 13:00:48.938458	Created from quotation	2025-05-14 14:04:24.465489	2025-05-21 13:00:48.939114	f
483	2	Κάρισσα Νάνα	Κάρισσα Νάνα	2L	2L	3	0	2025-05-22 17:23:36.17735	Created from quotation	2025-05-14 14:04:22.789213	2025-05-22 17:23:36.177947	f
376	2	Κάρυ	Helichrysum italicum	2L		2	0	2025-05-22 17:23:37.349824	Created from quotation	2025-04-29 17:52:59.758288	2025-05-22 17:23:37.350863	f
507	14	ΜΑΡΟΥΛΙΑ 1*12				1.5	0	2025-05-15 12:48:56.881862	Created from quotation	2025-05-15 12:48:56.882506	2025-05-15 12:48:56.882508	f
508	5	Arecastrum romanzoffianum	Arecastrum romanzoffianum		200/250cm-20L	45	30	2025-05-15 12:53:05.806789	Created from quotation	2025-05-15 12:53:05.807498	2025-05-15 12:53:05.8075	f
509	3	Lagerstroemia indica	Lagerstroemia indica	8-10 Girth	2m/6-8 Girth	85	65	2025-05-15 12:54:26.711752	Created from quotation	2025-05-15 12:54:26.712436	2025-05-15 12:54:26.712438	f
463	4	Laurus nobilis tree (pyramidal)	Laurus nobilis tree (pyramidal)	10-12 Girth	150cm	100	75	2025-05-15 12:55:26.955597	Created from quotation	2025-05-12 17:24:28.70676	2025-05-15 12:55:26.956563	f
510	9	ΜΑΝΤΑΡΙΝΙΑ	Citrus reticulata	8-10 Girth	20L/150cm-170cm	40	20	2025-05-15 13:02:23.473962	Created from quotation	2025-05-15 13:02:23.474688	2025-05-15 13:02:23.47469	f
511	9	ΠΟΡΤΟΚΑΛΙΑ	Citrus sinensis	8-10 Girth	20L/150cm-170cm	40	20	2025-05-15 13:02:56.621626	Created from quotation	2025-05-15 13:02:56.622238	2025-05-15 13:02:56.62224	f
512	4	ΠΕΥΚΟΣ ΗΜΕΡΟΣ	Pinus pinea		250/300cm/12-14 Girth	185	125	2025-05-15 13:07:47.861906	Created from quotation	2025-05-15 13:07:47.862556	2025-05-15 13:07:47.862558	f
513	4	ΑΡΤΥΜΑΤΙΑ	Schinus molle	10-12 Girth	200-250cm/10-12Girth	100	75	2025-05-15 13:11:05.923317	Created from quotation	2025-05-15 13:11:05.923966	2025-05-15 13:11:05.923968	f
514	4	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolia	10-12 Girth	200-250cm/ 10-12 Girth	100	75	2025-05-15 13:11:42.371079	Created from quotation	2025-05-15 13:11:42.371734	2025-05-15 13:11:42.371736	f
515	2	ΑΓΑΠΑΝΘΟΣ	Agapanthus africanus	2-3lit	10cm	3.5	0	2025-05-15 13:12:13.060232	Created from quotation	2025-05-15 13:12:13.060854	2025-05-15 13:12:13.060856	f
516	4	Duranta alba	Duranta alba	5lit	15cm/2L	3.5	2.5	2025-05-15 13:14:08.114116	Created from quotation	2025-05-15 13:14:08.114709	2025-05-15 13:14:08.11471	f
517	3	Σχοινια	Pistacia lentiscus	5lit	30cm/5L	8	0	2025-05-15 13:15:51.456327	Created from quotation	2025-05-15 13:15:51.456992	2025-05-15 13:15:51.456994	f
518	4	ΔΑΦΝΗ	Laurus nobilis	5lit	60cm	11	8	2025-05-15 13:19:23.499877	Created from quotation	2025-05-15 13:19:23.500509	2025-05-15 13:19:23.50051	f
519	4	Αγιόκλημα	Αγιόκλημα	1,5-1,7m		18	12	2025-05-15 13:26:19.283362	Created from quotation	2025-05-15 13:26:19.284003	2025-05-15 13:26:19.284005	f
520	5	Συκαμιά Άκαρπη				40	0	2025-05-15 13:41:00.84498	Created from quotation	2025-05-15 13:41:00.845662	2025-05-15 13:41:00.845664	f
526	2	Στεφανωτή	Στεφανωτή		2L	3.5	0	2025-05-18 09:42:18.363931	Created from quotation	2025-05-18 09:42:18.364521	2025-05-18 09:42:18.364522	f
528	2	Πιττόσπορο Ορθοκλαδο	Πιττόσπορο Ορθοκλαδο		2L	3	0	2025-05-18 09:42:19.629737	Created from quotation	2025-05-18 09:42:19.630574	2025-05-18 09:42:19.630575	f
529	2	Κάρισσα	Κάρισσα		2L	3	0	2025-05-18 09:42:20.049031	Created from quotation	2025-05-18 09:42:20.04979	2025-05-18 09:42:20.049792	f
530	2	Αλαίαγνος	Αλαίαγνος		2L	3.5	0	2025-05-18 09:42:20.485164	Created from quotation	2025-05-18 09:42:20.48593	2025-05-18 09:42:20.485932	f
531	2	Αλαίαγνος Διχρωμος	Αλαίαγνος Διχρωμος		2L	3.5	0	2025-05-18 09:42:20.90634	Created from quotation	2025-05-18 09:42:20.906974	2025-05-18 09:42:20.906976	f
532	2	Σχοινια 	Σχοινια 		2L	2.5	0	2025-05-18 09:42:21.331454	Created from quotation	2025-05-18 09:42:21.332092	2025-05-18 09:42:21.332094	f
533	2	Τουράντα Gold	Τουράντα Gold		2L	3	0	2025-05-18 09:42:21.754041	Created from quotation	2025-05-18 09:42:21.75467	2025-05-18 09:42:21.754672	f
534	2	Διέτης	Διέτης		2L	2.5	0	2025-05-18 09:42:22.168895	Created from quotation	2025-05-18 09:42:22.169523	2025-05-18 09:42:22.169525	f
535	2	Βιβούρνο Τίνους	Βιβούρνο Τίνους		2L	3.5	0	2025-05-18 09:42:22.587428	Created from quotation	2025-05-18 09:42:22.588043	2025-05-18 09:42:22.588044	f
536	2	Ευωνυμό	Ευωνυμό		2L	3	0	2025-05-18 09:42:23.009916	Created from quotation	2025-05-18 09:42:23.010587	2025-05-18 09:42:23.010588	f
537	2	Βιτεξ	Βιτεξ		2L	3	0	2025-05-18 09:42:23.432192	Created from quotation	2025-05-18 09:42:23.432819	2025-05-18 09:42:23.432821	f
522	2	Λεβάντα Κυπριακή	Λεβάντα Κυπριακή	2L	2L	2	0	2025-05-22 17:23:38.49477	Created from quotation	2025-05-18 09:42:16.681579	2025-05-22 17:23:38.49534	f
524	2	Ρίγανη	Ρίγανη	2L	2L	2	0	2025-05-22 17:23:39.24408	Created from quotation	2025-05-18 09:42:17.522667	2025-05-22 17:23:39.244954	f
523	2	Μελισσόχορτο	Μελισσόχορτο		2L	2	0	2025-05-18 09:43:32.85548	Created from quotation	2025-05-18 09:42:17.106437	2025-05-18 09:43:32.85596	f
525	2	Σαντολίνα	Σαντολίνα	2L	2L	2	0	2025-05-22 17:23:39.649997	Created from quotation	2025-05-18 09:42:17.946913	2025-05-22 17:23:39.650606	f
538	2	Πιττοσπορο ορθοκλαδο	Πιττοσπορο ορθοκλαδο		2L	3	0	2025-05-19 09:45:45.896747	Created from quotation	2025-05-19 09:45:45.89832	2025-05-19 09:45:45.898321	f
539	2	golden swanes 	golden swanes 		5L	8	0	2025-05-19 09:45:46.34515	Created from quotation	2025-05-19 09:45:46.345808	2025-05-19 09:45:46.345809	f
540	2	totem 	totem 		10L	15	0	2025-05-19 09:45:46.764141	Created from quotation	2025-05-19 09:45:46.765254	2025-05-19 09:45:46.765257	f
541	2	Strelitzia Reginae 	Strelitzia Reginae 		10L/2pcs	12	0	2025-05-19 09:45:47.209983	Created from quotation	2025-05-19 09:45:47.210715	2025-05-19 09:45:47.210716	f
542	2	Strelitzia Nicolae 	Strelitzia Nicolae 		5L	8	0	2025-05-19 09:45:47.614265	Created from quotation	2025-05-19 09:45:47.614887	2025-05-19 09:45:47.614889	f
543	2	agapanthus 	agapanthus 		2L	3.5	0	2025-05-19 09:45:48.094067	Created from quotation	2025-05-19 09:45:48.094866	2025-05-19 09:45:48.094868	f
544	2	arcontophoinix cumm 	arcontophoinix cumm 			25	0	2025-05-19 09:45:48.464822	Created from quotation	2025-05-19 09:45:48.465453	2025-05-19 09:45:48.465455	f
545	2	archontophoinix 	archontophoinix 			20	0	2025-05-19 09:45:48.831135	Created from quotation	2025-05-19 09:45:48.831861	2025-05-19 09:45:48.831863	f
546	2	royal palm 	royal palm 			0	0	2025-05-19 09:45:49.210892	Created from quotation	2025-05-19 09:45:49.211553	2025-05-19 09:45:49.211555	f
547	2	θουγια 	θουγια 			8	0	2025-05-19 09:45:49.604216	Created from quotation	2025-05-19 09:45:49.604865	2025-05-19 09:45:49.604867	f
549	2	λεμόνια 	λεμόνια 			15	0	2025-05-19 09:45:50.403558	Created from quotation	2025-05-19 09:45:50.404185	2025-05-19 09:45:50.404187	f
550	2	Σιεφλερα 	Σιεφλερα Αχτινοφυλλη		5L	8	0	2025-05-19 09:45:50.830901	Created from quotation	2025-05-19 09:45:50.831587	2025-05-19 09:45:50.831589	f
551	2	κλεμεντινη 	κλεμεντινη 			15	0	2025-05-19 09:45:51.193295	Created from quotation	2025-05-19 09:45:51.194029	2025-05-19 09:45:51.194031	f
552	2	μερσηνια 	μερσηνια 	5L		8	0	2025-05-19 09:45:51.580433	Created from quotation	2025-05-19 09:45:51.581071	2025-05-19 09:45:51.581073	f
553	2	Σιεφλερα δίχρωμη	Σιεφλερα δίχρωμη			0	0	2025-05-19 09:45:51.963386	Created from quotation	2025-05-19 09:45:51.964016	2025-05-19 09:45:51.964018	f
554	2	ΠΕΥΚΟΣ ΑΓΡΙΟΣ	Pinus halepensis	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		15	0	2025-05-19 13:23:45.775356	Created from quotation	2025-05-19 13:23:45.776924	2025-05-19 13:23:45.776926	f
527	2	Στρελίτσια Reginae	Στρελίτσια Reginae	5L/1pc	5L/1pc	6	0	2025-05-22 17:23:35.807887	Created from quotation	2025-05-18 09:42:18.785519	2025-05-22 17:23:35.809229	f
521	2	Λεβάντα Les Bleus Thierry	Λεβάντα Les Bleus Thierry	2L	2L	2	0	2025-05-22 17:23:38.113678	Created from quotation	2025-05-18 09:42:16.2604	2025-05-22 17:23:38.114426	f
555	2	ΚΟΚΚΙΝΟΦΥΛΛΗ	Prunus negra	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		0	0	2025-05-19 13:23:46.154068	Created from quotation	2025-05-19 13:23:46.154865	2025-05-19 13:23:46.154867	f
556	2	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolius (new)	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		0	0	2025-05-19 13:23:46.911312	Created from quotation	2025-05-19 13:23:46.912018	2025-05-19 13:23:46.91202	f
557	2	ΚΕΡΚΙΣ	Cercis	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		0	0	2025-05-19 13:23:47.315469	Created from quotation	2025-05-19 13:23:47.316255	2025-05-19 13:23:47.316257	f
558	13	ΚΥΠΑΡΙΣΣΙ	Cupressus sempervirens	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	1.50Μ/9	12	8	2025-05-19 13:23:47.734507	Created from quotation	2025-05-19 13:23:47.735235	2025-05-19 13:23:47.735237	f
559	2	ΤΖΙΑΚΑΡΑΝΤΑ	Jacaranda	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		0	0	2025-05-19 13:23:48.122032	Created from quotation	2025-05-19 13:23:48.123	2025-05-19 13:23:48.123002	f
560	2	Prunus laurocerasus	Prunus laurocerasus	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		0	0	2025-05-19 13:23:48.548456	Created from quotation	2025-05-19 13:23:48.549105	2025-05-19 13:23:48.549107	f
561	2	ΠΛΟΥΜΕΡΙΑ ΚΟΚΚΙΝΗ	Plumeria rubra	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		0	0	2025-05-19 13:23:48.937756	Created from quotation	2025-05-19 13:23:48.938747	2025-05-19 13:23:48.938749	f
563	2	ΚΙΣΣΟΣ	Hedera helix	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		0	0	2025-05-19 13:23:49.758727	Created from quotation	2025-05-19 13:23:49.759438	2025-05-19 13:23:49.75944	f
565	2	ΒΟΥΚΑΝΑΝΑ	Bougainvillea glabra	0,25m/2L		0	0	2025-05-19 13:23:51.046289	Created from quotation	2025-05-19 13:23:51.047075	2025-05-19 13:23:51.047078	f
567	2	ΔΙΕΤΗΣ	Dietes grandiflora	0,25m/2L		3	0	2025-05-19 13:23:51.807489	Created from quotation	2025-05-19 13:23:51.808128	2025-05-19 13:23:51.80813	f
581	2	ΠΕΥΚΟΣ ΑΓΡΙΟΣ	Pinus halepensis	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	1,5m/15L(3-4 Girth)	20	0	2025-05-21 13:06:45.640232	Created from quotation	2025-05-21 13:06:45.642566	2025-05-21 13:06:45.64257	f
562	2	ΜΑΚΝΟΛΙΑ	Magnolia grandiflora (new)	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		90	0	2025-05-21 13:07:29.130137	Created from quotation	2025-05-19 13:23:49.335039	2025-05-21 13:07:29.130762	f
566	2	ΤΕΚΟΜΑΡΙΑ ΠΟΡΤΟΚΑΛΙΑ	Tecomaria capensis	0,25m/2L		3.5	0	2025-05-19 13:32:37.246502	Created from quotation	2025-05-19 13:23:51.424186	2025-05-19 13:32:37.247005	f
564	2	ΚΑΡΙΣΣΑ	Carissa macrocarpa	0,25m/2L	10CM	4	0	2025-05-19 13:33:56.696324	Created from quotation	2025-05-19 13:23:50.646075	2025-05-19 13:33:56.696956	f
570	2	ΑΡΟΔΑΦΝΗ	Nerium oleander	0,25m/2L		3	0	2025-05-19 13:34:37.519656	Created from quotation	2025-05-19 13:23:52.966748	2025-05-19 13:34:37.520198	f
572	2	ΛΕΒΑΝΤΑ	Lavender angustifolia	0,25m/2L		2	0	2025-05-19 13:35:27.537258	Created from quotation	2025-05-19 13:23:54.130807	2025-05-19 13:35:27.53778	f
573	2	ΠΕΥΚΟΣ ΑΓΡΙΟΣ	Pinus halepensis	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	1,5m/15L	20	0	2025-05-19 13:41:07.38201	Created from quotation	2025-05-19 13:41:07.382672	2025-05-19 13:41:07.382674	f
582	3	ΜΑΚΝΟΛΙΑ	Magnolia grandiflora (new)	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	1.5M/4-6 Girth	90	65	2025-05-21 13:07:53.801418	Created from quotation	2025-05-21 13:07:53.802362	2025-05-21 13:07:53.802366	f
569	2	ΠΙΤΤΟΣΠΟΡΟ ΝΑΝΑ	Pittosporum tobira nana	0,25m/2L		3.5	0	2025-05-19 13:48:21.146332	Created from quotation	2025-05-19 13:23:52.576033	2025-05-19 13:48:21.146835	f
574	2	ΔΙΕΤΗΣ	Dietes grandiflora	0,25m/2L	20cm/2L	3	0	2025-05-19 13:49:13.80862	Created from quotation	2025-05-19 13:49:13.809649	2025-05-19 13:49:13.809651	f
588	6	Jacaranda	Jacaranda	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	1-2Girth/1.5-1.7m	30	10	2025-05-22 05:56:20.065657	Created from quotation	2025-05-22 05:56:20.066321	2025-05-22 05:56:20.066323	f
576	3	Δεντρο του Ιούδα	Cercis	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	1.5-1.8m	80	50	2025-05-20 13:27:26.132121	Created from quotation	2025-05-20 13:27:26.133066	2025-05-20 13:27:26.133069	f
575	3	Jacaranda	Jacaranda	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	3-4Girth	60	35	2025-05-20 13:34:34.012756	Created from quotation	2025-05-20 13:26:34.491947	2025-05-20 13:34:34.013898	f
577	12	Δεντρο του Ιούδα	Cercis	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	2-2.5m/2-4Girth	60	35	2025-05-20 13:35:46.730317	Created from quotation	2025-05-20 13:35:46.731076	2025-05-20 13:35:46.731078	f
578	12	Κισσός	Hedera helix	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	1.2-1.4m	8	4	2025-05-20 13:37:26.515049	Created from quotation	2025-05-20 13:36:29.42115	2025-05-20 13:37:26.51571	f
579	6	Plumeria rubra	Plumeria rubra	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	50cm/3L	8	5	2025-05-20 13:40:58.438315	Created from quotation	2025-05-20 13:40:58.439646	2025-05-20 13:40:58.43965	f
568	2	ΠΙΤΤΟΣΠΟΡΟ	Pittosporum tobira	0,25m/2L		3.5	0	2025-05-21 13:04:58.537752	Created from quotation	2025-05-19 13:23:52.202382	2025-05-21 13:04:58.53855	f
571	2	ΑΛΤΕΡΝΑΘΗΡΑ	Alternanthera	0,25m/2L		3.5	0	2025-05-21 13:05:13.824947	Created from quotation	2025-05-19 13:23:53.752531	2025-05-21 13:05:13.825635	f
548	2	αρτυματια	αρτυματια	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	10L	20	0	2025-05-21 13:06:05.712905	Created from quotation	2025-05-19 09:45:50.029582	2025-05-21 13:06:05.713495	f
589	2	Archontophoenix 	Archontophoenix 			10	0	2025-05-22 17:23:35.422557	Created from quotation	2025-05-22 17:23:35.425275	2025-05-22 17:23:35.425278	f
437	4	Κοκκινόφυλλη	PRUNUS CERASIFERA 'KRAUTER VESUVIUS'	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm		30	10	2025-05-22 05:53:21.31758	Created from quotation	2025-05-07 18:36:15.681025	2025-05-22 05:53:21.318659	f
586	6	Κοκκινόφυλλη	Prunus negra	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	150cm/1-2 Girth/10L	35	25	2025-05-22 05:54:24.532444	Created from quotation	2025-05-22 05:53:32.969152	2025-05-22 05:54:24.532951	f
587	9	Κοκκινόφυλλη	Prunus negra	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	160cm/1-2 Girth/25L	35	45	2025-05-22 05:54:56.271469	Created from quotation	2025-05-22 05:54:56.272102	2025-05-22 05:54:56.272104	f
591	2	Λεβαντούλα	Λεβαντούλα	2L		2	0	2025-05-22 17:23:38.873505	Created from quotation	2025-05-22 17:23:38.874666	2025-05-22 17:23:38.874669	f
590	2	Θούγια	Θούγια	2L		8	0	2025-05-22 17:33:07.457156	Created from quotation	2025-05-22 17:23:36.569159	2025-05-22 17:33:07.45774	f
592	11	Quercus robur	Quercus robur	200/250cm	8/10-2,5-3m	120	85	2025-05-25 10:17:23.478729	Created from quotation	2025-05-25 10:17:23.480233	2025-05-25 10:17:23.480235	f
593	11	Miscanthus sinensis 'Gracillimus'	Miscanthus sinensis 'Gracillimus'	100cm	3L	15.5	9.75	2025-05-25 10:17:24.155265	Created from quotation	2025-05-25 10:17:24.155813	2025-05-25 10:17:24.155815	f
594	11	Viburnum tinus	Viburnum tinus	60/80cm	5L	28.75	19.5	2025-05-25 10:17:24.808275	Created from quotation	2025-05-25 10:17:24.808785	2025-05-25 10:17:24.808787	f
584	2	Cupressus  sempervirens 'Totem'	Cupressus  sempervirens 'Totem'	8-10Girth		45	0	2025-05-25 10:48:55.104328	Created from quotation	2025-05-21 17:41:33.265169	2025-05-25 10:48:55.105237	f
585	2	Ficus lyrata	Ficus lyrata	150-200cm		1	0	2025-05-25 10:48:55.673471	Created from quotation	2025-05-21 17:41:33.858435	2025-05-25 10:48:55.67393	f
595	2	Morus nigra	Morus nigra	8-10Girth		45	0	2025-05-25 10:48:56.244828	Created from quotation	2025-05-25 10:48:56.246215	2025-05-25 10:48:56.246216	f
583	2	Arecastrum  romanzoffianum	Arecastrum  romanzoffianum	150-200cm		45	0	2025-05-25 10:48:54.531726	Created from quotation	2025-05-21 17:41:32.663419	2025-05-25 10:48:54.532603	f
596	2	Prunus cerasifera NIgra	Prunus cerasifera NIgra	8-10Girth		60	0	2025-05-25 10:48:58.041186	Created from quotation	2025-05-25 10:48:58.041702	2025-05-25 10:48:58.041703	f
597	2	Schinus terebinthifolia	Schinus terebinthifolia			52	0	2025-05-25 10:48:59.208865	Created from quotation	2025-05-25 10:48:59.209508	2025-05-25 10:48:59.209511	f
598	2	Dianella tasmanica	Dianella tasmanica	2lit		7	0	2025-05-25 10:49:00.363649	Created from quotation	2025-05-25 10:49:00.36437	2025-05-25 10:49:00.364371	f
599	2	Pennisetum setaceum 'Rubrum'	Pennisetum setaceum 'Rubrum'	2lit		3	0	2025-05-25 10:49:02.090998	Created from quotation	2025-05-25 10:49:02.091576	2025-05-25 10:49:02.091578	f
602	2	Philodendron xanadu	Philodendron xanadu	5-7lit		5	0	2025-05-25 10:49:05.513547	Created from quotation	2025-05-25 10:49:05.514215	2025-05-25 10:49:05.514217	f
603	2	Senecio mandraliscae	Senecio mandraliscae	2/3lit		2.5	0	2025-05-25 10:49:06.6647	Created from quotation	2025-05-25 10:49:06.665251	2025-05-25 10:49:06.665254	f
607	5	Arecastrum  romanzoffianum	Arecastrum  romanzoffianum		30L	45	35	2025-05-25 11:10:03.504898	Created from quotation	2025-05-25 11:10:03.505467	2025-05-25 11:10:03.505468	f
608	3	Cupressus  sempervirens 'Totem'	Cupressus  sempervirens 'Totem'	8-10Girth	170cm	45	35	2025-05-25 11:10:31.053525	Created from quotation	2025-05-25 11:10:31.054216	2025-05-25 11:10:31.054218	f
609	11	Ficus lyrata	Ficus lyrata			1	0	2025-05-25 11:10:44.897315	Created from quotation	2025-05-25 11:10:44.897873	2025-05-25 11:10:44.897875	f
610	9	Μουριά Άκαρπη	Morus nigra	8-10Girth	20L/150cm-170cm	45	30	2025-05-25 11:12:02.332765	Created from quotation	2025-05-25 11:12:02.333327	2025-05-25 11:12:02.333328	f
611	4	Prunus cerasifera NIgra	Prunus cerasifera NIgra	8-10Girth	180cm/6-8 Girth	60	45	2025-05-25 11:13:50.914003	Created from quotation	2025-05-25 11:13:50.914624	2025-05-25 11:13:50.914625	f
600	2	Agave attenuata	Agave attenuata	5/7lit		15	0	2025-05-25 11:18:50.348214	Created from quotation	2025-05-25 10:49:03.803497	2025-05-25 11:18:50.349118	f
601	2	Ligustrum japonicum	Ligustrum japonicum	5lit		7	0	2025-05-25 11:19:11.332741	Created from quotation	2025-05-25 10:49:04.945254	2025-05-25 11:19:11.333304	f
612	11	Senecio mandraliscae	Senecio mandraliscae	2/3lit	1L	2.5	0	2025-05-25 11:22:06.442462	Created from quotation	2025-05-25 11:22:06.442996	2025-05-25 11:22:06.442997	f
604	2	Strelitzia reginaea	Strelitzia reginaea	5-7lit		6	0	2025-05-25 11:22:30.174706	Created from quotation	2025-05-25 10:49:07.238723	2025-05-25 11:22:30.175278	f
605	2	Teucrium fruticans	Teucrium fruticans	3-5lit		2.5	0	2025-05-25 11:22:54.370443	Created from quotation	2025-05-25 10:49:07.807306	2025-05-25 11:22:54.370944	f
606	2	Viburnum Tinus 'Lucidum'	Viburnum Tinus 'Lucidum'	5/7lit		7	0	2025-05-25 11:23:11.927761	Created from quotation	2025-05-25 10:49:08.388498	2025-05-25 11:23:11.928287	f
481	2	Rosmarinus officinalis 'Prostratus'	Rosmarinus officinalis 'Prostratus'	2/3lit	20cm	2	0	2025-05-25 11:24:30.761403	Created from quotation	2025-05-12 17:24:42.474689	2025-05-25 11:24:30.761843	f
580	12	ΜΑΣΤΙΧΟΔΕΝΤΡΟ	Schinus terebinthifolius	1.50-1.80 m / 15-25 ltr pot /  trunk 4-5cm	2-2.5m/4-6Girth	26	20	2025-05-26 15:38:02.857877	Created from quotation	2025-05-20 13:42:59.351182	2025-05-26 15:38:02.859232	f
613	4	Γιαννης			7L/130cm	15	10	2025-05-27 08:37:58.182591	Created from quotation	2025-05-27 08:37:58.184252	2025-05-27 08:37:58.184256	f
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public."user" (id, username, password_hash, is_admin, created_at, last_login) FROM stdin;
1	admin	scrypt:32768:8:1$u8PkfPdbyg9s6R2M$9b5722b16ebe200a4f233e8ee0e4a2bc074c1d7e6955f30e84c16de068420eab5835327b7a514e58e7ed49db4001759f59e50c5f4faaf333f127718c6b46c96f	t	2025-04-01 17:32:00.927506	2025-05-28 11:47:38.867532
2	testuser	scrypt:32768:8:1$63OjZ2KrPZKkoPqX$82b37c670faa3534ed436bf3037ec8f485cd4561cfc2012058c2c97d53619f8a2cadcdabc23e643c39aeb6828bada32b3fb6d6c33b9fb5c12cf44600e6c670c8	t	2025-04-06 16:35:10.206109	2025-04-06 16:35:50.201462
\.


--
-- Name: company_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.company_settings_id_seq', 1, true);


--
-- Name: customer_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.customer_category_id_seq', 10, true);


--
-- Name: customer_contact_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.customer_contact_id_seq', 8, true);


--
-- Name: customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.customer_id_seq', 45, true);


--
-- Name: file_upload_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.file_upload_id_seq', 97, true);


--
-- Name: import_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.import_log_id_seq', 1, false);


--
-- Name: invoice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.invoice_id_seq', 27, true);


--
-- Name: invoice_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.invoice_item_id_seq', 185, true);


--
-- Name: lead_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.lead_id_seq', 1, false);


--
-- Name: order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.order_id_seq', 8, true);


--
-- Name: order_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.order_item_id_seq', 12, true);


--
-- Name: price_list_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.price_list_id_seq', 2700, true);


--
-- Name: price_list_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.price_list_item_id_seq', 1, false);


--
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.product_id_seq', 1980, true);


--
-- Name: product_update_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.product_update_request_id_seq', 14, true);


--
-- Name: quotation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.quotation_id_seq', 67, true);


--
-- Name: quotation_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.quotation_item_id_seq', 939, true);


--
-- Name: supplier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.supplier_id_seq', 18, true);


--
-- Name: supplier_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.supplier_product_id_seq', 613, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.user_id_seq', 2, true);


--
-- Name: company_settings company_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_settings
    ADD CONSTRAINT company_settings_pkey PRIMARY KEY (id);


--
-- Name: customer_category customer_category_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer_category
    ADD CONSTRAINT customer_category_pkey PRIMARY KEY (id);


--
-- Name: customer_contact customer_contact_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer_contact
    ADD CONSTRAINT customer_contact_pkey PRIMARY KEY (id);


--
-- Name: customer customer_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (id);


--
-- Name: file_upload file_upload_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.file_upload
    ADD CONSTRAINT file_upload_pkey PRIMARY KEY (id);


--
-- Name: import_log import_log_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.import_log
    ADD CONSTRAINT import_log_pkey PRIMARY KEY (id);


--
-- Name: invoice_addenda invoice_addenda_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_addenda
    ADD CONSTRAINT invoice_addenda_pkey PRIMARY KEY (id);


--
-- Name: invoice_addendum_lines invoice_addendum_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_addendum_lines
    ADD CONSTRAINT invoice_addendum_lines_pkey PRIMARY KEY (id);


--
-- Name: invoice invoice_invoice_number_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT invoice_invoice_number_key UNIQUE (invoice_number);


--
-- Name: invoice_item invoice_item_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_item
    ADD CONSTRAINT invoice_item_pkey PRIMARY KEY (id);


--
-- Name: invoice invoice_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT invoice_pkey PRIMARY KEY (id);


--
-- Name: lead lead_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.lead
    ADD CONSTRAINT lead_pkey PRIMARY KEY (id);


--
-- Name: order_item order_item_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item
    ADD CONSTRAINT order_item_pkey PRIMARY KEY (id);


--
-- Name: order order_order_number_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_order_number_key UNIQUE (order_number);


--
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- Name: price_list_item price_list_item_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list_item
    ADD CONSTRAINT price_list_item_pkey PRIMARY KEY (id);


--
-- Name: price_list price_list_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list
    ADD CONSTRAINT price_list_pkey PRIMARY KEY (id);


--
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- Name: product_update_request product_update_request_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product_update_request
    ADD CONSTRAINT product_update_request_pkey PRIMARY KEY (id);


--
-- Name: quotation_item quotation_item_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation_item
    ADD CONSTRAINT quotation_item_pkey PRIMARY KEY (id);


--
-- Name: quotation quotation_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation
    ADD CONSTRAINT quotation_pkey PRIMARY KEY (id);


--
-- Name: quotation quotation_quotation_number_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation
    ADD CONSTRAINT quotation_quotation_number_key UNIQUE (quotation_number);


--
-- Name: supplier supplier_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.supplier
    ADD CONSTRAINT supplier_name_key UNIQUE (name);


--
-- Name: supplier supplier_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.supplier
    ADD CONSTRAINT supplier_pkey PRIMARY KEY (id);


--
-- Name: supplier_product supplier_product_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.supplier_product
    ADD CONSTRAINT supplier_product_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: product_sku_unique_idx; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX product_sku_unique_idx ON public.product USING btree (sku) WHERE (sku IS NOT NULL);


--
-- Name: customer customer_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.customer_category(id);


--
-- Name: customer_contact customer_contact_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.customer_contact
    ADD CONSTRAINT customer_contact_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: file_upload file_upload_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.file_upload
    ADD CONSTRAINT file_upload_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: import_log import_log_imported_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.import_log
    ADD CONSTRAINT import_log_imported_by_fkey FOREIGN KEY (imported_by) REFERENCES public."user"(id);


--
-- Name: invoice_addenda invoice_addenda_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_addenda
    ADD CONSTRAINT invoice_addenda_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: invoice_addendum_lines invoice_addendum_lines_addendum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_addendum_lines
    ADD CONSTRAINT invoice_addendum_lines_addendum_id_fkey FOREIGN KEY (addendum_id) REFERENCES public.invoice_addenda(id);


--
-- Name: invoice invoice_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT invoice_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: invoice_item invoice_item_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_item
    ADD CONSTRAINT invoice_item_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoice(id);


--
-- Name: invoice_item invoice_item_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.invoice_item
    ADD CONSTRAINT invoice_item_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: lead lead_converted_to_quotation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.lead
    ADD CONSTRAINT lead_converted_to_quotation_id_fkey FOREIGN KEY (converted_to_quotation_id) REFERENCES public.quotation(id);


--
-- Name: order order_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: order_item order_item_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item
    ADD CONSTRAINT order_item_order_id_fkey FOREIGN KEY (order_id) REFERENCES public."order"(id);


--
-- Name: order_item order_item_price_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item
    ADD CONSTRAINT order_item_price_list_id_fkey FOREIGN KEY (price_list_id) REFERENCES public.price_list(id);


--
-- Name: order_item order_item_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.order_item
    ADD CONSTRAINT order_item_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: price_list price_list_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list
    ADD CONSTRAINT price_list_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: price_list_item price_list_item_price_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list_item
    ADD CONSTRAINT price_list_item_price_list_id_fkey FOREIGN KEY (price_list_id) REFERENCES public.price_list(id);


--
-- Name: price_list_item price_list_item_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list_item
    ADD CONSTRAINT price_list_item_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: price_list price_list_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.price_list
    ADD CONSTRAINT price_list_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: product_update_request product_update_request_price_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product_update_request
    ADD CONSTRAINT product_update_request_price_list_id_fkey FOREIGN KEY (price_list_id) REFERENCES public.price_list(id);


--
-- Name: product_update_request product_update_request_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.product_update_request
    ADD CONSTRAINT product_update_request_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: quotation quotation_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation
    ADD CONSTRAINT quotation_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(id);


--
-- Name: quotation_item quotation_item_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation_item
    ADD CONSTRAINT quotation_item_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(id);


--
-- Name: quotation_item quotation_item_quotation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation_item
    ADD CONSTRAINT quotation_item_quotation_id_fkey FOREIGN KEY (quotation_id) REFERENCES public.quotation(id);


--
-- Name: quotation_item quotation_item_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.quotation_item
    ADD CONSTRAINT quotation_item_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.supplier(id);


--
-- Name: supplier_product supplier_product_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.supplier_product
    ADD CONSTRAINT supplier_product_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.supplier(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

